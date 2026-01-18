import asyncio
from typing import List, Dict
from bs4 import BeautifulSoup
from database import Database


class ImageAltTextModule:
    """Module to detect images without alt attributes or with empty alt attributes"""
    
    def __init__(self, db: Database):
        """
        Initialize the Image Alt Text module.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def analyze(self, scan_id: int, pages: List[Dict]) -> List[Dict]:
        """
        Analyze website for images without alt attributes.
        
        Args:
            scan_id: Scan ID
            pages: List of pages from crawler
        
        Returns:
            List of image alt text issues found
        """
        issues = []
        
        for page in pages:
            if not page.get('html'):
                continue
                
            url = page['url']
            html = page['html']
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all img tags
            img_tags = soup.find_all('img')
            
            for img in img_tags:
                # Get the alt attribute
                alt_attr = img.get('alt', '')
                
                # Check if alt attribute is missing or empty
                if alt_attr is None or alt_attr.strip() == '':
                    # Get the src attribute for context
                    img_src = img.get('src', 'Unknown')
                    
                    issue = {
                        'issue_type': 'missing_alt_text',
                        'url': url,
                        'source_page': url,
                        'description': f'Image without alt attribute: {img_src}',
                        'severity': 'medium'
                    }
                    issues.append(issue)
                    self.db.add_issue(
                        scan_id=scan_id,
                        issue_type='missing_alt_text',
                        url=url,
                        source_page=url,
                        description=issue['description'],
                        severity='medium'
                    )
                elif len(alt_attr.strip()) < 5:  # Very short alt text (might be placeholder)
                    img_src = img.get('src', 'Unknown')
                    
                    issue = {
                        'issue_type': 'short_alt_text',
                        'url': url,
                        'source_page': url,
                        'description': f'Image with very short alt text: {img_src} (alt: "{alt_attr}")',
                        'severity': 'low'
                    }
                    issues.append(issue)
                    self.db.add_issue(
                        scan_id=scan_id,
                        issue_type='short_alt_text',
                        url=url,
                        source_page=url,
                        description=issue['description'],
                        severity='low'
                    )
        
        return issues