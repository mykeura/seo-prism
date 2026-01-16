from typing import List, Dict
from bs4 import BeautifulSoup
from database import Database


class MetaTagsModule:
    """Module to validate meta tags in crawled pages."""
    
    def __init__(self, db: Database):
        """
        Initialize the Meta Tags module.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def analyze(self, scan_id: int, crawled_pages: List[Dict]) -> List[Dict]:
        """
        Analyze crawled pages for missing meta tags.
        
        Args:
            scan_id: Scan ID
            crawled_pages: List of crawled page results
        
        Returns:
            List of meta tag issues
        """
        issues = []
        
        for page in crawled_pages:
            page_url = page['url']
            html = page.get('html')
            
            if not html:
                continue
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check for title tag
            title_tag = soup.find('title')
            if not title_tag or not title_tag.get_text().strip():
                issue = {
                    'issue_type': 'missing_title',
                    'url': page_url,
                    'source_page': page_url,
                    'description': 'Missing or empty <title> tag',
                    'severity': 'high'
                }
                issues.append(issue)
                
                # Add to database
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='missing_title',
                    url=page_url,
                    source_page=page_url,
                    description='Missing or empty <title> tag',
                    severity='high'
                )
            
            # Check for meta description
            meta_description = soup.find('meta', attrs={'name': 'description'})
            if not meta_description or not meta_description.get('content', '').strip():
                issue = {
                    'issue_type': 'missing_description',
                    'url': page_url,
                    'source_page': page_url,
                    'description': 'Missing or empty <meta name="description"> tag',
                    'severity': 'medium'
                }
                issues.append(issue)
                
                # Add to database
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='missing_description',
                    url=page_url,
                    source_page=page_url,
                    description='Missing or empty <meta name="description"> tag',
                    severity='medium'
                )
        
        return issues