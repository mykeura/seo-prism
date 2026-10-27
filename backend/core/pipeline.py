# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import asyncio
from typing import Dict, List, Optional

from core.crawler import Crawler
from core.issues import count_actionable_issues
from core.net_guard import NetworkGuard
from core.url_utils import normalize_url
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
from modules.spa_detection import SpaDetectionModule
from modules.standard_files import StandardFilesModule
from modules.structured_data import StructuredDataModule
from modules.thin_content import ThinContentModule


class ScanError(RuntimeError):
    """A target-level failure that callers must report, not grade."""

    status_code = 400


class ScanTargetUnreachable(ScanError):
    """The target could not be reached (network, timeout or 5xx)."""

    status_code = 502


class ScanBlockedByRobots(ScanError):
    """robots.txt disallowed the scan target itself."""

    status_code = 400


def _find_base_entry(crawled_pages: List[Dict], base_url: str) -> Optional[Dict]:
    base_normalized = normalize_url(base_url)
    for page in crawled_pages:
        if page.get('url') == base_normalized:
            return page
        if page.get('requested_url') == base_normalized:
            return page
    return None


def ensure_target_was_crawled(crawled_pages: List[Dict], base_url: str,
                              robots_skipped_urls) -> None:
    """Raise when a scan did not obtain a valid HTML page for its target.

    A dead host, a timeout, a 4xx/5xx root or a non-HTML target used to be
    graded as an F report with four "missing standard file" issues. None of
    those are something the site owner can fix, so they must become a
    target-level error instead of a scan result.
    """
    base_normalized = normalize_url(base_url)

    if base_normalized in robots_skipped_urls:
        raise ScanBlockedByRobots(
            f"robots.txt disallows the scan target '{base_url}'")

    entry = _find_base_entry(crawled_pages, base_url)
    if entry is None:
        raise ScanError(f"Could not fetch the scan target '{base_url}'")

    status = entry.get('status', 0)
    if status == 0:
        detail = entry.get('error') or 'connection failed'
        raise ScanTargetUnreachable(f"Could not reach '{base_url}': {detail}")
    if status == 408:
        raise ScanTargetUnreachable(f"Timed out while fetching '{base_url}'")
    if status >= 500:
        raise ScanTargetUnreachable(
            f"Target '{base_url}' returned HTTP {status}")
    if status >= 400:
        raise ScanError(f"Target '{base_url}' returned HTTP {status}")

    html = entry.get('html')
    if not html or not html.strip():
        raise ScanError(
            f"No HTML content found at '{base_url}' (HTTP {status})")


def is_error_response(page: Dict) -> bool:
    """
    True when a crawled entry is an error response rather than a real page.

    Anything outside 2xx/3xx (404/410/5xx, timeouts reported as 408, and
    connection failures reported as status 0) is not content the site owner
    published as a page, even when the server answered with an HTML error
    body.
    """
    return not (200 <= page.get('status', 0) < 400)


def discard_error_page_content(crawled_pages: List[Dict]) -> None:
    """
    Strip the body, links and resources of error responses, in place.

    Servers usually answer a missing URL with an HTML error document. Left
    untouched, that document is analysed as if it were a real page: it gets
    flagged for a short title, a missing description, thin content or a
    duplicated H1, and it inflates the page count. A single broken link then
    produced a whole cascade of bogus issues and dragged the grade down.

    The entry itself (url + status) is kept: the broken-link and canonical
    checks read the status of the pages they point to.
    """
    for page in crawled_pages:
        if is_error_response(page):
            page['html'] = None
            page['links'] = []
            page['resources'] = []


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


def _analyze_page_modules(db: Database, scan_id: int,
                          crawled_pages: List[Dict]) -> List[Dict]:
    """Run the CPU-bound page modules off the event loop."""
    issues = []
    for module in _page_modules(db):
        issues.extend(module.analyze(scan_id, crawled_pages))
    return issues


def _analyze_site(db: Database, scan_id: int, crawled_pages: List[Dict],
                  url: str) -> tuple[List[Dict], Dict]:
    """Run the remaining sync modules plus resource accounting off-loop."""
    issues = []
    issues.extend(OrphanPagesModule(db).analyze(scan_id, crawled_pages, url))
    issues.extend(SpaDetectionModule(db).analyze(scan_id, crawled_pages, url))

    resource_analysis = ResourceAnalyzer().analyze_resources(crawled_pages)

    # Drop cached parse trees; the raw page dicts stay intact.
    for page in crawled_pages:
        page.pop('_soup', None)

    return issues, resource_analysis


async def run_scan_pipeline(db: Database, url: str, max_pages: int,
                            ignore_robots: bool,
                            guard: Optional[NetworkGuard] = None) -> Dict:
    """
    Run a full SEO scan: crawl, store results, run every analysis module
    and compute the SEO grade. Shared by the CLI and the HTTP API.

    Args:
        db: Database instance (caller owns it and must close it)
        url: Target URL to scan
        max_pages: Maximum pages to crawl
        ignore_robots: Whether to ignore robots.txt
        guard: SSRF guard; defaults to the operator's environment setting

    Returns:
        Dict with 'scan_id', 'crawled_pages', 'issues', 'seo_grade',
        'resource_analysis', 'html_page_count' and 'robots_skipped'
    """
    if guard is None:
        guard = NetworkGuard.from_env()

    async with Crawler(url, ignore_robots=ignore_robots, guard=guard) as crawler:
        crawled_pages = await crawler.crawl(max_pages=max_pages)
    robots_skipped = crawler.robots_skipped_count

    # Do this before creating the scan row: a dead or blocked target must not
    # leave a phantom F report in the history.
    ensure_target_was_crawled(
        crawled_pages, url, crawler.robots_skipped_urls)

    scan_id = db.create_scan(url)

    # A 404 page is not a page of the site: drop its content before it is
    # stored, analysed or counted (see discard_error_page_content).
    discard_error_page_content(crawled_pages)

    db.store_crawled_pages(scan_id, crawled_pages)

    # Parsing and analysing every page is CPU-bound: keep it on a worker
    # thread so the event loop can still answer /health (and other requests)
    # while a scan runs. The connection is only used sequentially: the loop
    # awaits each worker call before touching the database again.
    issues = await asyncio.to_thread(
        _analyze_page_modules, db, scan_id, crawled_pages)

    # Modules whose analyze() signature differs from the standard one.
    # StandardFiles performs network I/O, so it stays on the event loop.
    issues.extend(await StandardFilesModule(db, guard=guard).analyze(scan_id, url))

    site_issues, resource_analysis = await asyncio.to_thread(
        _analyze_site, db, scan_id, crawled_pages, url)
    issues.extend(site_issues)

    html_page_count = resource_analysis['html_pages']

    total_issues = count_actionable_issues(issues)
    info_notices = len(issues) - total_issues
    db.update_scan_totals(scan_id, html_page_count, total_issues)

    seo_grade = SEOGradeCalculator().calculate_grade(html_page_count, issues)

    return {
        'scan_id': scan_id,
        'crawled_pages': crawled_pages,
        'issues': issues,
        'total_issues': total_issues,
        'info_notices': info_notices,
        'seo_grade': seo_grade,
        'resource_analysis': resource_analysis,
        'html_page_count': html_page_count,
        'robots_skipped': robots_skipped,
    }
