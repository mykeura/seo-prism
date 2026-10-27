# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

from typing import List, Dict, Set
from urllib.parse import urlparse
from core.url_utils import normalize_url
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
        
        root_urls = {normalize_url(base_url)}
        pages_by_url = {}
        for page in crawled_pages:
            if page.get('is_resource', False) or page.get('is_redirect', False):
                continue
            page_url = page['url']
            if page_url not in pages_by_url:
                pages_by_url[page_url] = page
        
        if not pages_by_url:
            return issues
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT DISTINCT target_url 
            FROM links l
            JOIN pages p ON l.page_id = p.id
            WHERE p.scan_id = ?
        ''', (scan_id,))
        
        linked_urls = set(row['target_url'] for row in cursor.fetchall())
        
        base_url_clean = self._get_base_url(base_url)
        
        for page_url, page in pages_by_url.items():
            requested_url = page.get('requested_url')
            if page_url in root_urls or requested_url in root_urls:
                continue
            if self._is_homepage(page_url, base_url_clean):
                continue
            if page_url in linked_urls:
                continue
            # A redirect target is linked through the URL that redirects to
            # it; the requested URL is what appears as the link target.
            if requested_url and requested_url in linked_urls:
                continue

            issue = {
                'issue_type': 'orphan_page',
                'url': page_url,
                'source_page': None,
                'description': 'Page has no incoming internal links',
                'severity': 'medium'
            }
            issues.append(issue)
            
            self.db.add_issue(
                scan_id=scan_id,
                issue_type='orphan_page',
                url=page_url,
                source_page=None,
                description='Page has no incoming internal links',
                severity='medium'
            )
        
        return issues
