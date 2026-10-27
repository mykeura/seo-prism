# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import asyncio
from typing import List, Dict
from database import Database
from core.soup import soup_for


class DuplicateContentModule:
    """Module to detect duplicate titles and descriptions across pages"""
    
    def __init__(self, db: Database):
        """
        Initialize the Duplicate Content module.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def analyze(self, scan_id: int, pages: List[Dict]) -> List[Dict]:
        """
        Analyze website for duplicate titles and descriptions.
        
        Args:
            scan_id: Scan ID
            pages: List of pages from crawler
        
        Returns:
            List of duplicate content issues found
        """
        issues = []
        
        titles = {}
        descriptions = {}
        
        for page in pages:
            if not page.get('html'):
                continue
                
            url = page['url']

            soup = soup_for(page)

            title_tag = soup.find('title')
            title_match = title_tag.get_text().strip() if title_tag else None

            meta_desc = soup.find(
                'meta', attrs={'name': lambda value: value and value.lower() == 'description'})
            desc_match = meta_desc.get('content', '').strip() if meta_desc and meta_desc.get('content') else None
            
            if title_match:
                if title_match not in titles:
                    titles[title_match] = []
                titles[title_match].append(url)
            
            if desc_match:
                if desc_match not in descriptions:
                    descriptions[desc_match] = []
                descriptions[desc_match].append(url)
        
        for title, urls in titles.items():
            if len(urls) > 1:
                for url in urls:
                    issue = {
                        'issue_type': 'duplicate_title',
                        'url': url,
                        'source_page': url,
                        'description': f'Duplicate title found across {len(urls)} pages: "{title[:50]}{"..." if len(title) > 50 else ""}"',
                        'severity': 'medium'
                    }
                    issues.append(issue)
                    self.db.add_issue(
                        scan_id=scan_id,
                        issue_type='duplicate_title',
                        url=url,
                        source_page=url,
                        description=issue['description'],
                        severity='medium'
                    )
        
        for desc, urls in descriptions.items():
            if len(urls) > 1:
                for url in urls:
                    issue = {
                        'issue_type': 'duplicate_description',
                        'url': url,
                        'source_page': url,
                        'description': f'Duplicate meta description found across {len(urls)} pages: "{desc[:50]}{"..." if len(desc) > 50 else ""}"',
                        'severity': 'medium'
                    }
                    issues.append(issue)
                    self.db.add_issue(
                        scan_id=scan_id,
                        issue_type='duplicate_description',
                        url=url,
                        source_page=url,
                        description=issue['description'],
                        severity='medium'
                    )
        
        return issues