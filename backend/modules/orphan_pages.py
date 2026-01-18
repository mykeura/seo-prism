from typing import List, Dict, Set
from urllib.parse import urlparse
from database import Database


class OrphanPagesModule:
    """Module to detect orphan pages (pages with no incoming links)."""
    
    def __init__(self, db: Database):
        """
        Initialize the Orphan Pages module.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def _get_base_url(self, url: str) -> str:
        """
        Extract base URL (scheme + netloc) from a URL.
        
        Args:
            url: URL to extract base from
        
        Returns:
            Base URL
        """
        try:
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}"
        except Exception:
            return url
    
    def _is_homepage(self, page_url: str, base_url: str) -> bool:
        """
        Check if a URL is the homepage.
        
        Args:
            page_url: Page URL to check
            base_url: Base URL of the site
        
        Returns:
            True if homepage, False otherwise
        """
        try:
            parsed = urlparse(page_url)
            path = parsed.path.rstrip('/')
            return path == '' or path == '/' or path == '/index.html'
        except Exception:
            return False
    
    def analyze(self, scan_id: int, crawled_pages: List[Dict], base_url: str) -> List[Dict]:
        """
        Analyze crawled pages for orphan pages (pages with no incoming links).
        
        Args:
            scan_id: Scan ID
            crawled_pages: List of crawled page results
            base_url: Base URL of the scanned site
        
        Returns:
            List of orphan page issues
        """
        issues = []
        
        # Get all crawled page URLs
        crawled_urls = set()
        for page in crawled_pages:
            if not page.get('is_resource', False):  # Only HTML pages
                crawled_urls.add(page['url'])
        
        if not crawled_urls:
            return issues
        
        # Get all target URLs from links (pages that are linked to)
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT DISTINCT target_url 
            FROM links l
            JOIN pages p ON l.page_id = p.id
            WHERE p.scan_id = ?
        ''', (scan_id,))
        
        linked_urls = set(row['target_url'] for row in cursor.fetchall())
        
        # Find orphan pages (crawled but not linked to)
        base_url_clean = self._get_base_url(base_url)
        
        for page_url in crawled_urls:
            # Skip homepage (it's normal to not have internal links to it)
            if self._is_homepage(page_url, base_url_clean):
                continue
            
            # Check if page has any incoming links
            if page_url not in linked_urls:
                # This is an orphan page
                issue = {
                    'issue_type': 'orphan_page',
                    'url': page_url,
                    'source_page': None,
                    'description': 'Page has no incoming internal links',
                    'severity': 'medium'
                }
                issues.append(issue)
                
                # Add to database
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='orphan_page',
                    url=page_url,
                    source_page=None,
                    description='Page has no incoming internal links',
                    severity='medium'
                )
        
        return issues