import asyncio
from typing import List, Dict
from database import Database


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
        
        # Extract titles and descriptions from all pages
        titles = {}
        descriptions = {}
        
        for page in pages:
            if not page.get('html'):
                continue
                
            url = page['url']
            html = page['html']
            
            # Extract title
            title_match = None
            if '<title>' in html and '</title>' in html:
                start = html.find('<title>') + len('<title>')
                end = html.find('</title>', start)
                if start != -1 and end != -1:
                    title_match = html[start:end].strip()
            
            # Extract meta description
            desc_match = None
            if 'name="description"' in html or 'name=\'description\'' in html:
                # Look for <meta name="description" content="...">
                import re
                desc_pattern = r'<meta[^>]+name[\s]*=[\s]*["\']description["\'][^>]+content[\s]*=[\s]*["\']([^"\']*)["\'][^>]*>'
                match = re.search(desc_pattern, html, re.IGNORECASE)
                if match:
                    desc_match = match.group(1).strip()
                
                # Alternative pattern for description meta tag
                if not desc_match:
                    desc_pattern_alt = r'<meta[^>]+content[\s]*=[\s]*["\']([^"\']*)["\'][^>]+name[\s]*=[\s]*["\']description["\'][^>]*>'
                    match = re.search(desc_pattern_alt, html, re.IGNORECASE)
                    if match:
                        desc_match = match.group(1).strip()
            
            # Store titles and descriptions with their URLs
            if title_match:
                if title_match not in titles:
                    titles[title_match] = []
                titles[title_match].append(url)
            
            if desc_match:
                if desc_match not in descriptions:
                    descriptions[desc_match] = []
                descriptions[desc_match].append(url)
        
        # Find duplicates
        for title, urls in titles.items():
            if len(urls) > 1:  # More than one page has the same title
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
            if len(urls) > 1:  # More than one page has the same description
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