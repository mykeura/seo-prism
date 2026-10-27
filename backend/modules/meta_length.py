# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

from typing import List, Dict
from core.soup import soup_for
from database import Database


class MetaLengthModule:
    """Module to analyze the length of title tags and meta descriptions."""
    
    TITLE_MIN_LENGTH = 30
    TITLE_MAX_LENGTH = 60
    
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
            
            soup = soup_for(page)
            
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else ''
            
            if title:
                title_length = len(title)
                
                if title_length < self.TITLE_MIN_LENGTH:
                    issue = {
                        'issue_type': 'title_too_short',
                        'url': page_url,
                        'source_page': page_url,
                        'description': f'Title is too short ({title_length} characters). Recommended: {self.TITLE_MIN_LENGTH}-{self.TITLE_MAX_LENGTH} characters',
                        'severity': 'medium'
                    }
                    issues.append(issue)
                    
                    self.db.add_issue(
                        scan_id=scan_id,
                        issue_type='title_too_short',
                        url=page_url,
                        source_page=page_url,
                        description=f'Title is too short ({title_length} characters). Recommended: {self.TITLE_MIN_LENGTH}-{self.TITLE_MAX_LENGTH} characters',
                        severity='medium'
                    )
                
                elif title_length > self.TITLE_MAX_LENGTH:
                    issue = {
                        'issue_type': 'title_too_long',
                        'url': page_url,
                        'source_page': page_url,
                        'description': f'Title is too long ({title_length} characters). Recommended: {self.TITLE_MIN_LENGTH}-{self.TITLE_MAX_LENGTH} characters',
                        'severity': 'medium'
                    }
                    issues.append(issue)
                    
                    self.db.add_issue(
                        scan_id=scan_id,
                        issue_type='title_too_long',
                        url=page_url,
                        source_page=page_url,
                        description=f'Title is too long ({title_length} characters). Recommended: {self.TITLE_MIN_LENGTH}-{self.TITLE_MAX_LENGTH} characters',
                        severity='medium'
                    )
            
            meta_description = soup.find(
                'meta', attrs={'name': lambda value: value and value.lower() == 'description'})
            description = meta_description.get('content', '').strip() if meta_description else ''
            
            if description:
                desc_length = len(description)
                
                if desc_length < self.META_DESC_MIN_LENGTH:
                    issue = {
                        'issue_type': 'meta_description_too_short',
                        'url': page_url,
                        'source_page': page_url,
                        'description': f'Meta description is too short ({desc_length} characters). Recommended: {self.META_DESC_MIN_LENGTH}-{self.META_DESC_MAX_LENGTH} characters',
                        'severity': 'medium'
                    }
                    issues.append(issue)
                    
                    self.db.add_issue(
                        scan_id=scan_id,
                        issue_type='meta_description_too_short',
                        url=page_url,
                        source_page=page_url,
                        description=f'Meta description is too short ({desc_length} characters). Recommended: {self.META_DESC_MIN_LENGTH}-{self.META_DESC_MAX_LENGTH} characters',
                        severity='medium'
                    )
                
                elif desc_length > self.META_DESC_MAX_LENGTH:
                    issue = {
                        'issue_type': 'meta_description_too_long',
                        'url': page_url,
                        'source_page': page_url,
                        'description': f'Meta description is too long ({desc_length} characters). Recommended: {self.META_DESC_MIN_LENGTH}-{self.META_DESC_MAX_LENGTH} characters',
                        'severity': 'medium'
                    }
                    issues.append(issue)
                    
                    self.db.add_issue(
                        scan_id=scan_id,
                        issue_type='meta_description_too_long',
                        url=page_url,
                        source_page=page_url,
                        description=f'Meta description is too long ({desc_length} characters). Recommended: {self.META_DESC_MIN_LENGTH}-{self.META_DESC_MAX_LENGTH} characters',
                        severity='medium'
                    )
        
        return issues