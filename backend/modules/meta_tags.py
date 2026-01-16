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
        Analyze crawled pages for missing and duplicate meta tags.
        
        Args:
            scan_id: Scan ID
            crawled_pages: List of crawled page results
        
        Returns:
            List of meta tag issues
        """
        issues = []
        
        # First pass: collect all titles and descriptions
        page_titles = {}
        page_descriptions = {}
        
        for page in crawled_pages:
            page_url = page['url']
            html = page.get('html')
            
            if not html:
                continue
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else ''
            
            # Extract description
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '').strip() if meta_description else ''
            
            page_titles[page_url] = title
            page_descriptions[page_url] = description
        
        # Find duplicate titles
        title_counts = {}
        for url, title in page_titles.items():
            if title:  # Only check non-empty titles
                title_counts[title] = title_counts.get(title, 0) + 1
        
        # Find duplicate descriptions
        description_counts = {}
        for url, description in page_descriptions.items():
            if description:  # Only check non-empty descriptions
                description_counts[description] = description_counts.get(description, 0) + 1
        
        # Second pass: check for missing tags and create issues
        for page in crawled_pages:
            page_url = page['url']
            html = page.get('html')
            
            if not html:
                continue
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check for title tag
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else ''
            
            if not title:
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
            elif title_counts.get(title, 0) > 1:
                # Duplicate title
                issue = {
                    'issue_type': 'duplicate_title',
                    'url': page_url,
                    'source_page': page_url,
                    'description': f'Duplicate title: "{title}"',
                    'severity': 'medium'
                }
                issues.append(issue)
                
                # Add to database
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='duplicate_title',
                    url=page_url,
                    source_page=page_url,
                    description=f'Duplicate title: "{title}"',
                    severity='medium'
                )
            
            # Check for meta description
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '').strip() if meta_description else ''
            
            if not description:
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
            elif description_counts.get(description, 0) > 1:
                # Duplicate description
                issue = {
                    'issue_type': 'duplicate_description',
                    'url': page_url,
                    'source_page': page_url,
                    'description': f'Duplicate description: "{description}"',
                    'severity': 'low'
                }
                issues.append(issue)
                
                # Add to database
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='duplicate_description',
                    url=page_url,
                    source_page=page_url,
                    description=f'Duplicate description: "{description}"',
                    severity='low'
                )
        
        return issues