# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

from typing import Dict, List

from core.crawler import Crawler
from database import Database
from modules.broken_links import BrokenLinksModule
from modules.canonical_tags import CanonicalTagsModule
from modules.duplicate_content import DuplicateContentModule
from modules.hreflang import HreflangModule
from modules.image_alt_text import ImageAltTextModule
from modules.meta_length import MetaLengthModule
from modules.meta_robots import MetaRobotsModule
from modules.meta_tags import MetaTagsModule
from modules.orphan_pages import OrphanPagesModule
from modules.resource_analyzer import ResourceAnalyzer
from modules.seo_grade import SEOGradeCalculator
from modules.standard_files import StandardFilesModule
from modules.structured_data import StructuredDataModule
from modules.thin_content import ThinContentModule


def _page_modules(db: Database) -> List:
    """Analysis modules with the standard analyze(scan_id, crawled_pages) signature."""
    return [
        BrokenLinksModule(db),
        MetaTagsModule(db),
        MetaRobotsModule(db),
        HreflangModule(db),
        DuplicateContentModule(db),
        ImageAltTextModule(db),
        CanonicalTagsModule(db),
        StructuredDataModule(db),
        MetaLengthModule(db),
        ThinContentModule(db),
    ]


async def run_scan_pipeline(db: Database, url: str, max_pages: int,
                            ignore_robots: bool) -> Dict:
    """
    Run a full SEO scan: crawl, store results, run every analysis module
    and compute the SEO grade. Shared by the CLI and the HTTP API.

    Args:
        db: Database instance (caller owns it and must close it)
        url: Target URL to scan
        max_pages: Maximum pages to crawl
        ignore_robots: Whether to ignore robots.txt

    Returns:
        Dict with 'scan_id', 'crawled_pages', 'issues', 'seo_grade',
        'resource_analysis' and 'html_page_count'
    """
    scan_id = db.create_scan(url)

    async with Crawler(url, ignore_robots=ignore_robots) as crawler:
        crawled_pages = await crawler.crawl(max_pages=max_pages)

    db.store_crawled_pages(scan_id, crawled_pages)

    issues = []
    for module in _page_modules(db):
        issues.extend(module.analyze(scan_id, crawled_pages))

    # Modules whose analyze() signature differs from the standard one
    issues.extend(await StandardFilesModule(db).analyze(scan_id, url))
    issues.extend(OrphanPagesModule(db).analyze(scan_id, crawled_pages, url))

    # Drop cached parse trees; the raw page dicts stay intact
    for page in crawled_pages:
        page.pop('_soup', None)

    resource_analyzer = ResourceAnalyzer()
    resource_analysis = resource_analyzer.analyze_resources(crawled_pages)
    html_page_count = resource_analysis['html_pages']

    db.update_scan_totals(scan_id, html_page_count, len(issues))

    seo_grade = SEOGradeCalculator().calculate_grade(html_page_count, issues)

    return {
        'scan_id': scan_id,
        'crawled_pages': crawled_pages,
        'issues': issues,
        'seo_grade': seo_grade,
        'resource_analysis': resource_analysis,
        'html_page_count': html_page_count,
    }
