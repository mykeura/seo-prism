import asyncio
import click
from core.crawler import Crawler
from core.url_utils import is_local, validate_url
from database import Database
from modules.broken_links import BrokenLinksModule
from modules.meta_tags import MetaTagsModule
from modules.standard_files import StandardFilesModule
from modules.missing_alt_tags import MissingAltTagsModule


@click.command()
@click.option('--url', required=True, help='Target URL to scan')
@click.option('--max-pages', default=100, help='Maximum number of pages to crawl')
def scan(url: str, max_pages: int):
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
    standard_files_module = StandardFilesModule(db)
    missing_alt_tags_module = MissingAltTagsModule(db)
    
    broken_link_issues = broken_links_module.analyze(scan_id, crawled_pages)
    meta_tag_issues = meta_tags_module.analyze(scan_id, crawled_pages)
    standard_files_issues = await standard_files_module.analyze(scan_id, url)
    missing_alt_tags_issues = missing_alt_tags_module.analyze(scan_id, crawled_pages)
    
    # Update scan totals
    total_issues = len(broken_link_issues) + len(meta_tag_issues) + len(standard_files_issues) + len(missing_alt_tags_issues)
    db.update_scan_totals(scan_id, len(crawled_pages), total_issues)
    
    # Get complete results
    results = db.get_scan_results(scan_id)
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
    
    click.echo()
    click.echo("=" * 60)
    click.echo("📊 SCAN RESULTS")
    click.echo("=" * 60)
    click.echo(f"🌐 URL: {scan.get('url', 'N/A')}")
    click.echo(f"📅 Scan Time: {scan.get('timestamp', 'N/A')}")
    click.echo(f"📄 Pages Analyzed: {scan.get('total_pages', 0)}")
    click.echo(f"⚠️  Total Issues: {scan.get('total_issues', 0)}")
    click.echo()
    
    if issues:
        # Group issues by type
        broken_links = [i for i in issues if i['issue_type'] == 'broken_link']
        missing_titles = [i for i in issues if i['issue_type'] == 'missing_title']
        missing_descriptions = [i for i in issues if i['issue_type'] == 'missing_description']
        
        # Display broken links
        if broken_links:
            click.echo("🔗 Broken Links:")
            for issue in broken_links:
                click.echo(f"   • {issue['url']} (in {issue['source_page']}) - {issue['description']}")
            click.echo()
        
        # Display missing titles
        if missing_titles:
            click.echo("📝 Missing Titles:")
            for issue in missing_titles:
                click.echo(f"   • {issue['url']}")
            click.echo()
        
        # Display missing descriptions
        if missing_descriptions:
            click.echo("📄 Missing Descriptions:")
            for issue in missing_descriptions:
                click.echo(f"   • {issue['url']}")
            click.echo()
    else:
        click.echo("✅ No issues found!")
        click.echo()
    
    click.echo("=" * 60)


def main():
    """Entry point for CLI."""
    scan()


if __name__ == '__main__':
    main()