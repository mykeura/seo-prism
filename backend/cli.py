import asyncio
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
from modules import h1_analysis
from modules import header_hierarchy
from modules.seo_grade import SEOGradeCalculator
from modules.resource_analyzer import ResourceAnalyzer
from modules.report_generator import SEOReportGenerator


@click.command()
@click.option('--url', required=True, help='Target URL to scan')
@click.option('--max-pages', default=100, help='Maximum number of pages to crawl')
@click.option('--generate-report', is_flag=True, help='Generate professional SEO report in PowerPoint format')
@click.option('--lang', default='en', type=click.Choice(['en', 'es']), help='Report language (en or es)')
@click.option('--output', default='seo_report.pptx', help='Output file path for the report')
def scan(url: str, max_pages: int, generate_report: bool, lang: str, output: str):
    """
    Scan a website for SEO issues.
    
    Example:
        poetry run scan --url http://localhost:3000
        poetry run scan --url https://example.com --max-pages 50
    """
    # Validate URL
    if not validate_url(url):
        click.echo(f"❌ Invalid URL: {url}", err=True)
        return
    
    # Check if local
    is_local_url = is_local(url)
    ignore_robots = is_local_url
    
    if is_local_url:
        click.echo("✅ Scanning in fast mode (ignoring robots.txt)")
    else:
        click.echo("⚠️  Scanning remote URL (respecting robots.txt)")
    
    click.echo(f"🔍 Starting scan of: {url}")
    
    # Run scan
    try:
        results = asyncio.run(run_scan(url, max_pages, ignore_robots))
        
        # Display results
        display_results(results)
        
        # Generate report if requested
        if generate_report:
            click.echo()
            click.echo(f"📊 Generating {lang.upper()} professional report...")
            
            try:
                report_generator = SEOReportGenerator()
                report_path = report_generator.generate_report(results, output, lang)
                click.echo(f"✅ Report generated: {report_path}")
                click.echo(f"💡 You can now edit the report in PowerPoint and export to PDF when ready.")
            except Exception as e:
                click.echo(f"❌ Error generating report: {e}", err=True)
        
    except Exception as e:
        click.echo(f"❌ Error during scan: {e}", err=True)


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
    
    # Analyze H1 headers and header hierarchy using functions
    all_pages_data = {page['url']: page for page in crawled_pages}
    h1_issues = []
    header_hierarchy_issues = []
    
    for page in crawled_pages:
        if page.get('html'):
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page['html'], 'html.parser')
            
            # H1 analysis
            page_h1_issues = h1_analysis.analyze_h1_headers(soup, page['url'], all_pages_data)
            h1_issues.extend(page_h1_issues)
            
            # Header hierarchy analysis
            page_hierarchy_issues = header_hierarchy.analyze_header_hierarchy(soup, page['url'])
            header_hierarchy_issues.extend(page_hierarchy_issues)
    
    # Update scan totals
    total_issues = len(broken_link_issues) + len(meta_tag_issues) + len(meta_robots_issues) + len(hreflang_issues) + len(standard_files_issues) + len(duplicate_content_issues) + len(image_alt_text_issues) + len(h1_issues) + len(header_hierarchy_issues) + len(canonical_issues) + len(orphan_pages_issues) + len(structured_data_issues) + len(meta_length_issues) + len(thin_content_issues)
    
    # Analyze resources to get actual HTML page count
    resource_analyzer = ResourceAnalyzer()
    resource_analysis = resource_analyzer.analyze_resources(crawled_pages)
    html_page_count = resource_analysis['html_pages']
    
    db.update_scan_totals(scan_id, html_page_count, total_issues)
    
    # Calculate SEO grade
    all_issues = broken_link_issues + meta_tag_issues + meta_robots_issues + hreflang_issues + standard_files_issues + duplicate_content_issues + image_alt_text_issues + h1_issues + header_hierarchy_issues + canonical_issues + orphan_pages_issues + structured_data_issues + meta_length_issues + thin_content_issues
    grade_calculator = SEOGradeCalculator()
    seo_grade = grade_calculator.calculate_grade(html_page_count, all_issues)
    
    # Get complete results
    results = db.get_scan_results(scan_id)
    results['seo_grade'] = seo_grade
    results['resource_analysis'] = resource_analysis
    db.close()
    
    return results


def display_results(results: dict):
    """
    Display scan results in terminal.
    
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
        # Group issues by type
        broken_links = [i for i in issues if i['issue_type'] == 'broken_link']
        missing_titles = [i for i in issues if i['issue_type'] == 'missing_title']
        missing_descriptions = [i for i in issues if i['issue_type'] == 'missing_description']
        duplicate_titles = [i for i in issues if i['issue_type'] == 'duplicate_title']
        duplicate_descriptions = [i for i in issues if i['issue_type'] == 'duplicate_description']
        missing_alt_tags = [i for i in issues if i['issue_type'] in ['missing_alt_tag', 'missing_alt_text', 'short_alt_text']]
        missing_h1 = [i for i in issues if i['issue_type'] == 'missing_h1']
        multiple_h1 = [i for i in issues if i['issue_type'] == 'multiple_h1_same_page']
        duplicate_h1 = [i for i in issues if i['issue_type'] == 'duplicate_h1']
        invalid_hierarchy = [i for i in issues if i['issue_type'] == 'invalid_header_hierarchy']
        meta_robots_issues = [i for i in issues if i['issue_type'].startswith('meta_robots')]
        hreflang_issues = [i for i in issues if i['issue_type'].startswith('hreflang')]
        standard_files_issues = [i for i in issues if i['issue_type'] in ['missing_robots_txt', 'missing_security_txt', 'missing_sitemap', 'missing_llms_txt']]
        
        # Display broken links
        if broken_links:
            click.echo("🔗 Broken Links:")
            for issue in broken_links[:10]:
                click.echo(f"   • {issue['url']} (in {issue['source_page']}) - {issue['description']}")
            if len(broken_links) > 10:
                click.echo(f"   ... and {len(broken_links) - 10} more")
            click.echo()
        
        # Display missing titles
        if missing_titles:
            click.echo("📝 Missing Titles:")
            for issue in missing_titles[:10]:
                click.echo(f"   • {issue['url']}")
            if len(missing_titles) > 10:
                click.echo(f"   ... and {len(missing_titles) - 10} more")
            click.echo()
        
        # Display missing descriptions
        if missing_descriptions:
            click.echo("📄 Missing Descriptions:")
            for issue in missing_descriptions[:10]:
                click.echo(f"   • {issue['url']}")
            if len(missing_descriptions) > 10:
                click.echo(f"   ... and {len(missing_descriptions) - 10} more")
            click.echo()
        
        # Display duplicate content
        if duplicate_titles or duplicate_descriptions:
            click.echo("📋 Duplicate Content:")
            if duplicate_titles:
                click.echo(f"   • {len(duplicate_titles)} pages with duplicate titles")
            if duplicate_descriptions:
                click.echo(f"   • {len(duplicate_descriptions)} pages with duplicate descriptions")
            click.echo()
        
        # Display image alt issues
        if missing_alt_tags:
            click.echo("🖼️  Images Without Alt Tags:")
            click.echo(f"   • {len(missing_alt_tags)} images missing alt text")
            click.echo()
        
        # Display H1 issues
        if missing_h1 or multiple_h1 or duplicate_h1:
            click.echo("🏷️  H1 Header Issues:")
            if missing_h1:
                click.echo(f"   • {len(missing_h1)} pages missing H1 header")
            if multiple_h1:
                click.echo(f"   • {len(multiple_h1)} pages with multiple H1 headers")
            if duplicate_h1:
                click.echo(f"   • {len(duplicate_h1)} pages with duplicate H1 headers")
            click.echo()
        
        # Display header hierarchy issues
        if invalid_hierarchy:
            click.echo("📐 Invalid Header Hierarchy:")
            click.echo(f"   • {len(invalid_hierarchy)} pages with invalid header structure")
            click.echo()
        
        # Display meta robots issues
        if meta_robots_issues:
            click.echo("🤖 Meta Robots Issues:")
            click.echo(f"   • {len(meta_robots_issues)} meta robots directive issues")
            click.echo()
        
        # Display hreflang issues
        if hreflang_issues:
            click.echo("🌍 Hreflang Issues:")
            click.echo(f"   • {len(hreflang_issues)} hreflang validation issues")
            click.echo()
        
        # Display standard files found
        found_standard_files = [i for i in issues if i['issue_type'] in ['robots_txt_found', 'security_txt_found', 'sitemap_found', 'llms_txt_found']]
        if found_standard_files:
            click.echo("📁 Standard Files Found:")
            for issue in found_standard_files:
                file_name = issue['issue_type'].replace('_found', '').replace('_', '.')
                click.echo(f"   • {file_name}: {issue['url']}")
            click.echo()
        
        # Display canonical issues
        canonical_chains = [i for i in issues if i['issue_type'] == 'canonical_chain']
        canonical_404 = [i for i in issues if i['issue_type'] == 'canonical_to_404']
        canonical_redirect = [i for i in issues if i['issue_type'] == 'canonical_to_redirect']
        canonical_variations = [i for i in issues if i['issue_type'] == 'canonical_url_variation']
        missing_canonical = [i for i in issues if i['issue_type'] == 'missing_canonical']
        
        if canonical_chains or canonical_404 or canonical_redirect or canonical_variations or missing_canonical:
            click.echo("🔗 Canonical Tag Issues:")
            if canonical_chains:
                click.echo(f"   • {len(canonical_chains)} canonical chain(s) detected")
            if canonical_404:
                click.echo(f"   • {len(canonical_404)} canonical(s) pointing to 404 pages")
            if canonical_redirect:
                click.echo(f"   • {len(canonical_redirect)} canonical(s) pointing to redirects")
            if canonical_variations:
                click.echo(f"   • {len(canonical_variations)} canonical(s) with URL variations")
            if missing_canonical:
                click.echo(f"   • {len(missing_canonical)} pages missing canonical tags")
            click.echo()
        
        # Display standard files issues
        if standard_files_issues:
            click.echo("📁 Standard Files Missing:")
            for issue in standard_files_issues:
                click.echo(f"   • {issue['issue_type']}")
            click.echo()
        
        # Display structured data issues
        missing_structured_data = [i for i in issues if i['issue_type'] == 'missing_structured_data']
        json_ld_issues = [i for i in issues if i['issue_type'].startswith('json_ld')]
        microdata_issues = [i for i in issues if i['issue_type'].startswith('microdata')]
        rdfa_issues = [i for i in issues if i['issue_type'].startswith('rdfa')]
        
        if missing_structured_data or json_ld_issues or microdata_issues or rdfa_issues:
            click.echo("📊 Structured Data Issues:")
            if missing_structured_data:
                click.echo(f"   • {len(missing_structured_data)} pages without structured data")
                for issue in missing_structured_data[:10]:
                    click.echo(f"      - {issue['url']}")
                if len(missing_structured_data) > 10:
                    click.echo(f"      ... and {len(missing_structured_data) - 10} more")
            if json_ld_issues:
                click.echo(f"   • {len(json_ld_issues)} JSON-LD issue(s)")
                for issue in json_ld_issues[:5]:
                    click.echo(f"      - {issue['description']}")
                if len(json_ld_issues) > 5:
                    click.echo(f"      ... and {len(json_ld_issues) - 5} more")
            if microdata_issues:
                click.echo(f"   • {len(microdata_issues)} Microdata issue(s)")
                for issue in microdata_issues[:5]:
                    click.echo(f"      - {issue['description']}")
                if len(microdata_issues) > 5:
                    click.echo(f"      ... and {len(microdata_issues) - 5} more")
            if rdfa_issues:
                click.echo(f"   • {len(rdfa_issues)} RDFa issue(s)")
                for issue in rdfa_issues[:5]:
                    click.echo(f"      - {issue['description']}")
                if len(rdfa_issues) > 5:
                    click.echo(f"      ... and {len(rdfa_issues) - 5} more")
            click.echo()
        
        # Display thin content issues
        thin_content = [i for i in issues if i['issue_type'] == 'thin_content']
        if thin_content:
            click.echo("📄 Thin Content Issues:")
            click.echo(f"   • {len(thin_content)} pages with thin content")
            for issue in thin_content[:10]:
                click.echo(f"      - {issue['url']}")
            if len(thin_content) > 10:
                click.echo(f"      ... and {len(thin_content) - 10} more")
            click.echo()
        
        # Display orphan pages
        orphan_pages = [i for i in issues if i['issue_type'] == 'orphan_page']
        if orphan_pages:
            click.echo("📁 Orphan Pages (no incoming links):")
            for issue in orphan_pages[:10]:
                click.echo(f"   • {issue['url']}")
            if len(orphan_pages) > 10:
                click.echo(f"   ... and {len(orphan_pages) - 10} more")
            click.echo()
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