from typing import List, Dict
from bs4 import BeautifulSoup
from database import Database


class MetaLengthModule:
    """Module to analyze the length of title tags and meta descriptions."""
    
    # Length thresholds for title tags
    TITLE_MIN_LENGTH = 30
    TITLE_MAX_LENGTH = 60
    
    # Length thresholds for meta descriptions
    META_DESC_MIN_LENGTH = 70
    META_DESC_MAX_LENGTH = 150
    
    def __init__(self, db: Database):
        """
        Initialize the Meta Length module.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def analyze(self, scan_id: int, crawled_pages: List[Dict]) -> List[Dict]:
        """
        Analyze crawled pages for title and meta description length issues.
        
        Args:
            scan_id: Scan ID
            crawled_pages: List of crawled page results
        
        Returns:
            List of meta length issues
        """
        issues = []
        
        for page in crawled_pages:
            page_url = page['url']
            html = page.get('html')
            
            if not html:
                continue
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Analyze title tag length
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else ''
            
            if title:
                title_length = len(title)
                
                # Check if title is too short
                if title_length < self.TITLE_MIN_LENGTH:
                    issue = {
                        'issue_type': 'title_too_short',
                        'url': page_url,
                        'source_page': page_url,
                        'description': f'Title is too short ({title_length} characters). Recommended: {self.TITLE_MIN_LENGTH}-{self.TITLE_MAX_LENGTH} characters',
                        'severity': 'medium'
                    }
                    issues.append(issue)
                    
                    # Add to database
                    self.db.add_issue(
                        scan_id=scan_id,
                        issue_type='title_too_short',
                        url=page_url,
                        source_page=page_url,
                        description=f'Title is too short ({title_length} characters). Recommended: {self.TITLE_MIN_LENGTH}-{self.TITLE_MAX_LENGTH} characters',
                        severity='medium'
                    )
                
                # Check if title is too long
                elif title_length > self.TITLE_MAX_LENGTH:
                    issue = {
                        'issue_type': 'title_too_long',
                        'url': page_url,
                        'source_page': page_url,
                        'description': f'Title is too long ({title_length} characters). Recommended: {self.TITLE_MIN_LENGTH}-{self.TITLE_MAX_LENGTH} characters',
                        'severity': 'medium'
                    }
                    issues.append(issue)
                    
                    # Add to database
                    self.db.add_issue(
                        scan_id=scan_id,
                        issue_type='title_too_long',
                        url=page_url,
                        source_page=page_url,
                        description=f'Title is too long ({title_length} characters). Recommended: {self.TITLE_MIN_LENGTH}-{self.TITLE_MAX_LENGTH} characters',
                        severity='medium'
                    )
            
            # Analyze meta description length
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '').strip() if meta_description else ''
            
            if description:
                desc_length = len(description)
                
                # Check if description is too short
                if desc_length < self.META_DESC_MIN_LENGTH:
                    issue = {
                        'issue_type': 'meta_description_too_short',
                        'url': page_url,
                        'source_page': page_url,
                        'description': f'Meta description is too short ({desc_length} characters). Recommended: {self.META_DESC_MIN_LENGTH}-{self.META_DESC_MAX_LENGTH} characters',
                        'severity': 'medium'
                    }
                    issues.append(issue)
                    
                    # Add to database
                    self.db.add_issue(
                        scan_id=scan_id,
                        issue_type='meta_description_too_short',
                        url=page_url,
                        source_page=page_url,
                        description=f'Meta description is too short ({desc_length} characters). Recommended: {self.META_DESC_MIN_LENGTH}-{self.META_DESC_MAX_LENGTH} characters',
                        severity='medium'
                    )
                
                # Check if description is too long
                elif desc_length > self.META_DESC_MAX_LENGTH:
                    issue = {
                        'issue_type': 'meta_description_too_long',
                        'url': page_url,
                        'source_page': page_url,
                        'description': f'Meta description is too long ({desc_length} characters). Recommended: {self.META_DESC_MIN_LENGTH}-{self.META_DESC_MAX_LENGTH} characters',
                        'severity': 'medium'
                    }
                    issues.append(issue)
                    
                    # Add to database
                    self.db.add_issue(
                        scan_id=scan_id,
                        issue_type='meta_description_too_long',
                        url=page_url,
                        source_page=page_url,
                        description=f'Meta description is too long ({desc_length} characters). Recommended: {self.META_DESC_MIN_LENGTH}-{self.META_DESC_MAX_LENGTH} characters',
                        severity='medium'
                    )
        
        return issues