import asyncio
import json
import click
from core.crawler import Crawler
from core.url_utils import is_local, validate_url
from database import Database
from modules.broken_links import BrokenLinksModule
from modules.meta_tags import MetaTagsModule
from modules.meta_robots import MetaRobotsModule
from modules.hreflang import HreflangModule
from modules.standard_files import StandardFilesModule
from modules.duplicate_content import DuplicateContentModule
from modules.image_alt_text import ImageAltTextModule
from modules.canonical_tags import CanonicalTagsModule
from modules.orphan_pages import OrphanPagesModule
from modules.structured_data import StructuredDataModule
from modules.meta_length import MetaLengthModule
from modules.thin_content import ThinContentModule
from modules.seo_grade import SEOGradeCalculator
from modules.resource_analyzer import ResourceAnalyzer
from modules.report_generator import SEOReportGenerator
from modules.pdf_report_generator import SEOReportPDFGenerator


@click.command()
@click.option('--url', required=True, help='Target URL to scan')
@click.option('--max-pages', default=100, help='Maximum number of pages to crawl')
@click.option('--json', 'as_json', is_flag=True, help='Print complete scan results as JSON to stdout (progress messages go to stderr)')
@click.option('--generate-report', is_flag=True, help='Generate professional SEO report (PDF by default, PowerPoint optional)')
@click.option('--report-format', 'report_format', default='pdf', type=click.Choice(['pdf', 'pptx']), help='Report format: pdf (default, complete and print-ready) or pptx (editable)')
@click.option('--lang', default='en', type=click.Choice(['en', 'es']), help='Report language (en or es)')
@click.option('--output', default=None, help='Output file path for the report (default: seo_report.pdf or seo_report.pptx per format)')
def scan(url: str, max_pages: int, as_json: bool, generate_report: bool, report_format: str, lang: str, output: str):
    """
    Scan a website for SEO issues.

    Example:
        poetry run scan --url http://localhost:3000
        poetry run scan --url https://example.com --max-pages 50
        poetry run scan --url https://example.com --json > results.json
    """
    # In --json mode every human-readable message goes to stderr so that
    # stdout carries ONLY the machine-readable JSON payload.
    if as_json:
        def echo(message=None, err=False):
            click.echo(message, err=True)
    else:
        def echo(message=None, err=False):
            click.echo(message, err=err)

    # Validate URL
    if not validate_url(url):
        echo(f"❌ Invalid URL: {url}", err=True)
        return

    # Check if local
    is_local_url = is_local(url)
    ignore_robots = is_local_url

    if is_local_url:
        echo("✅ Scanning in fast mode (ignoring robots.txt)")
    else:
        echo("⚠️  Scanning remote URL (respecting robots.txt)")

    echo(f"🔍 Starting scan of: {url}")

    # Run scan
    try:
        results = asyncio.run(run_scan(url, max_pages, ignore_robots))

        if as_json:
            payload = {
                'scan': results.get('scan', {}),
                'issues': results.get('issues', []),
                'seo_grade': results.get('seo_grade', {}),
                'resource_analysis': results.get('resource_analysis', {}),
            }
            click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            # Display results
            display_results(results)

        # Generate report if requested
        if generate_report:
            if output is None:
                output = 'seo_report.pdf' if report_format == 'pdf' else 'seo_report.pptx'

            echo()
            echo(f"📊 Generating {lang.upper()} professional report ({report_format.upper()})...")

            try:
                if report_format == 'pdf':
                    report_generator = SEOReportPDFGenerator()
                else:
                    report_generator = SEOReportGenerator()
                report_path = report_generator.generate_report(results, output, lang)
                echo(f"✅ Report generated: {report_path}")
                if report_format == 'pptx':
                    echo(f"💡 You can now edit the report in PowerPoint and export to PDF when ready.")
            except Exception as e:
                echo(f"❌ Error generating report: {e}", err=True)

    except Exception as e:
        echo(f"❌ Error during scan: {e}", err=True)


async def run_scan(url: str, max_pages: int, ignore_robots: bool) -> dict:
    """
    Execute the scan asynchronously.

    Args:
        url: Target URL
        max_pages: Maximum pages to crawl
        ignore_robots: Whether to ignore robots.txt

    Returns:
        Scan results dictionary
    """
    # Initialize database
    db = Database()

    # Create scan record
    scan_id = db.create_scan(url)

    # Crawl website
    async with Crawler(url, ignore_robots=ignore_robots) as crawler:
        crawled_pages = await crawler.crawl(max_pages=max_pages)

    # Store pages in database
    for page in crawled_pages:
        page_id = db.add_page(
            scan_id=scan_id,
            url=page['url'],
            status=page['status'],
            html=page.get('html')
        )

        # Store links
        for link in page.get('links', []):
            db.add_link(page_id, link, page['url'])

    # Run analysis modules
    broken_links_module = BrokenLinksModule(db)
    meta_tags_module = MetaTagsModule(db)
    meta_robots_module = MetaRobotsModule(db)
    hreflang_module = HreflangModule(db)
    standard_files_module = StandardFilesModule(db)
    duplicate_content_module = DuplicateContentModule(db)
    image_alt_text_module = ImageAltTextModule(db)
    canonical_tags_module = CanonicalTagsModule(db)
    orphan_pages_module = OrphanPagesModule(db)
    structured_data_module = StructuredDataModule(db)
    meta_length_module = MetaLengthModule(db)
    thin_content_module = ThinContentModule(db)

    broken_link_issues = broken_links_module.analyze(scan_id, crawled_pages)
    meta_tag_issues = meta_tags_module.analyze(scan_id, crawled_pages)
    meta_robots_issues = meta_robots_module.analyze(scan_id, crawled_pages)
    hreflang_issues = hreflang_module.analyze(scan_id, crawled_pages)
    standard_files_issues = await standard_files_module.analyze(scan_id, url)
    duplicate_content_issues = duplicate_content_module.analyze(scan_id, crawled_pages)
    image_alt_text_issues = image_alt_text_module.analyze(scan_id, crawled_pages)
    canonical_issues = canonical_tags_module.analyze(scan_id, crawled_pages)
    orphan_pages_issues = orphan_pages_module.analyze(scan_id, crawled_pages, url)
    structured_data_issues = structured_data_module.analyze(scan_id, crawled_pages)
    meta_length_issues = meta_length_module.analyze(scan_id, crawled_pages)
    thin_content_issues = thin_content_module.analyze(scan_id, crawled_pages)

    # NOTE: H1 issues (missing_h1, multiple_h1_same_page, duplicate_h1) and
    # header hierarchy issues (invalid_header_hierarchy) are already detected
    # and persisted to the database by MetaTagsModule, so no extra pass is
    # performed here. This keeps scan.total_issues == len(results['issues']).

    # Update scan totals
    total_issues = len(broken_link_issues) + len(meta_tag_issues) + len(meta_robots_issues) + len(hreflang_issues) + len(standard_files_issues) + len(duplicate_content_issues) + len(image_alt_text_issues) + len(canonical_issues) + len(orphan_pages_issues) + len(structured_data_issues) + len(meta_length_issues) + len(thin_content_issues)

    # Analyze resources to get actual HTML page count
    resource_analyzer = ResourceAnalyzer()
    resource_analysis = resource_analyzer.analyze_resources(crawled_pages)
    html_page_count = resource_analysis['html_pages']

    db.update_scan_totals(scan_id, html_page_count, total_issues)

    # Calculate SEO grade
    all_issues = broken_link_issues + meta_tag_issues + meta_robots_issues + hreflang_issues + standard_files_issues + duplicate_content_issues + image_alt_text_issues + canonical_issues + orphan_pages_issues + structured_data_issues + meta_length_issues + thin_content_issues
    grade_calculator = SEOGradeCalculator()
    seo_grade = grade_calculator.calculate_grade(html_page_count, all_issues)

    # Get complete results
    results = db.get_scan_results(scan_id)
    results['seo_grade'] = seo_grade
    results['resource_analysis'] = resource_analysis
    db.close()

    return results


# Ordered display categories: (section title, exact issue types, issue type prefixes).
# Every issue_type that does not match any category is shown under "Other Issues",
# so no failure is ever hidden.
_ISSUE_CATEGORIES = [
    ('🔗 Broken Links & Resources:',
     ('broken_link', 'broken_image', 'broken_script', 'broken_stylesheet'),
     ()),
    ('📝 Missing Titles:',
     ('missing_title',),
     ()),
    ('📄 Missing Descriptions:',
     ('missing_description',),
     ()),
    ('📏 Meta Length Issues:',
     ('title_too_long', 'title_too_short', 'meta_description_too_long', 'meta_description_too_short'),
     ()),
    ('📋 Duplicate Content:',
     ('duplicate_title', 'duplicate_description'),
     ()),
    ('🖼️  Images Without Alt Text:',
     ('missing_alt_tag', 'missing_alt_text', 'short_alt_text'),
     ()),
    ('🏷️  H1 Header Issues:',
     ('missing_h1', 'multiple_h1_same_page', 'duplicate_h1'),
     ()),
    ('📐 Invalid Header Hierarchy:',
     ('invalid_header_hierarchy',),
     ()),
    ('🤖 Meta Robots Issues:',
     ('meta_robots_noindex', 'meta_robots_nofollow', 'meta_robots_noarchive',
      'meta_robots_nosnippet', 'meta_robots_noimageindex', 'meta_robots_notranslate',
      'meta_robots_unavailable_after'),
     ('meta_robots_',)),
    ('🌍 Hreflang Issues:',
     ('hreflang_invalid_code', 'hreflang_duplicate_code', 'hreflang_missing_x_default',
      'hreflang_missing_self_reference', 'hreflang_missing_return_link',
      'hreflang_missing_canonical'),
     ('hreflang_',)),
    ('📁 Standard Files Missing:',
     ('missing_robots_txt', 'missing_security_txt', 'missing_sitemap', 'missing_llms_txt'),
     ()),
    ('🔗 Canonical Tag Issues:',
     ('canonical_chain', 'canonical_to_404', 'canonical_to_redirect',
      'canonical_url_variation', 'missing_canonical', 'empty_canonical'),
     ()),
    ('📊 Structured Data Issues:',
     ('missing_structured_data', 'json_ld_invalid_json', 'json_ld_missing_properties',
      'json_ld_missing_type', 'json_ld_short_headline', 'json_ld_unknown_type',
      'microdata_missing_type', 'microdata_unknown_type', 'rdfa_unknown_type'),
     ('json_ld_', 'microdata_', 'rdfa_')),
    ('📄 Thin Content Issues:',
     ('thin_content',),
     ()),
    ('📁 Orphan Pages (no incoming links):',
     ('orphan_page',),
     ()),
]

_STANDARD_FILES_FOUND_TYPES = ('robots_txt_found', 'security_txt_found', 'sitemap_found', 'llms_txt_found')


def _group_issues_by_type(issues: list) -> dict:
    """
    Group a flat issue list into {issue_type: [issues...]} preserving order.

    Args:
        issues: Flat list of issue dictionaries

    Returns:
        Dictionary of issue_type -> list of issues (in original order)
    """
    groups = {}
    for issue in issues:
        groups.setdefault(issue.get('issue_type', 'unknown'), []).append(issue)
    return groups


def _format_issue(issue: dict, show_source: bool = True, show_type: bool = False) -> str:
    """
    Format a single issue as '[issue_type] url (in source_page) - description'.

    Args:
        issue: Issue dictionary
        show_source: Whether to include the source page
        show_type: Whether to prefix the raw issue_type (used for unknown types)

    Returns:
        Formatted issue line
    """
    parts = []
    if show_type:
        parts.append(f"[{issue.get('issue_type', 'unknown')}]")
    parts.append(issue.get('url') or 'N/A')
    if show_source and issue.get('source_page'):
        parts.append(f"(in {issue['source_page']})")
    if issue.get('description'):
        parts.append(f"- {issue['description']}")
    return ' '.join(parts)


def _print_issue_section(title: str, issues: list, show_source: bool = True,
                         show_type: bool = False):
    """
    Print a full issue section: header plus EVERY issue, without truncation.

    Args:
        title: Section title (with emoji)
        issues: Issues belonging to the section
        show_source: Whether to include the source page in each line
        show_type: Whether to prefix each line with the raw issue_type
    """
    click.echo(f"{title} ({len(issues)}):")
    for issue in issues:
        click.echo(f"   • {_format_issue(issue, show_source=show_source, show_type=show_type)}")
    click.echo()


def _print_standard_files_found(issues: list):
    """
    Print the "Standard Files Found" informational section.

    Args:
        issues: Issues whose type is one of *_found
    """
    click.echo(f"📁 Standard Files Found ({len(issues)}):")
    for issue in issues:
        file_name = issue['issue_type'].replace('_found', '').replace('_', '.')
        click.echo(f"   • {file_name}: {issue.get('url', 'N/A')}")
    click.echo()


def display_results(results: dict):
    """
    Display scan results in terminal.

    Every issue found is printed in full (url + source_page + description),
    with no truncation and no "... and N more" summaries. Any issue_type
    without a dedicated section falls through to "Other Issues".

    Args:
        results: Scan results dictionary
    """
    scan = results.get('scan', {})
    issues = results.get('issues', [])
    seo_grade = results.get('seo_grade', {})
    resource_analysis = results.get('resource_analysis', {})

    click.echo()
    click.echo("=" * 60)
    click.echo("📊 SCAN RESULTS")
    click.echo("=" * 60)
    click.echo(f"🌐 URL: {scan.get('url', 'N/A')}")
    click.echo(f"📅 Scan Time: {scan.get('timestamp', 'N/A')}")
    click.echo(f"📄 Pages Analyzed: {scan.get('total_pages', 0)}")
    click.echo(f"⚠️  Total Issues: {scan.get('total_issues', 0)}")

    # Display SEO grade
    if seo_grade:
        grade = seo_grade.get('grade', 'N/A')
        score = seo_grade.get('score', 0)
        grade_color = _get_grade_color_ansi(grade)
        click.echo(f"🎯 SEO Grade: {grade_color}{grade} ({score}%)\033[0m")

    # Display resource analysis
    if resource_analysis:
        click.echo()
        click.echo("📦 Resources Found:")
        click.echo(f"   • HTML Pages: {resource_analysis['html_pages']}")
        click.echo(f"   • CSS Files: {resource_analysis['css_files']}")
        click.echo(f"   • JavaScript Files: {resource_analysis['js_files']}")
        click.echo(f"   • Images: {resource_analysis['images']}")
        click.echo(f"   • Other Resources: {resource_analysis['other_resources']}")
        click.echo(f"   • Total Resources: {resource_analysis['total_resources']}")

    click.echo()

    if issues:
        groups = _group_issues_by_type(issues)
        covered_types = set()

        # Dedicated sections (fixed order), each showing every single issue
        for title, exact_types, prefixes in _ISSUE_CATEGORIES:
            section_issues = []
            for issue_type, type_issues in groups.items():
                if issue_type in exact_types or any(issue_type.startswith(prefix) for prefix in prefixes):
                    section_issues.extend(type_issues)
                    covered_types.add(issue_type)
            if section_issues:
                _print_issue_section(title, section_issues)

        # Informational section: standard files that were found
        found_standard_files = [
            issue
            for issue_type in _STANDARD_FILES_FOUND_TYPES
            for issue in groups.get(issue_type, [])
        ]
        covered_types.update(_STANDARD_FILES_FOUND_TYPES)
        if found_standard_files:
            _print_standard_files_found(found_standard_files)

        # Safety net: any issue_type not covered above is listed here
        other_issues = [
            issue
            for issue_type, type_issues in groups.items()
            if issue_type not in covered_types
            for issue in type_issues
        ]
        if other_issues:
            _print_issue_section('🧩 Other Issues:', other_issues, show_type=True)
    else:
        click.echo("✅ No issues found!")
        click.echo()

    click.echo("=" * 60)


def main():
    """Entry point for CLI."""
    scan()


def _get_grade_color_ansi(grade: str) -> str:
    """
    Get ANSI color code for grade display in terminal.

    Args:
        grade: Grade letter ('A', 'B', 'C', 'D', 'F')

    Returns:
        ANSI color code
    """
    colors = {
        'A': '\033[92m',  # Green
        'B': '\033[94m',  # Blue
        'C': '\033[93m',  # Yellow
        'D': '\033[95m',  # Orange/Magenta
        'F': '\033[91m'   # Red
    }
    return colors.get(grade, '\033[0m')


if __name__ == '__main__':
    main()
