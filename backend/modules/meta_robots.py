from bs4 import BeautifulSoup
from typing import List, Dict
from database import Database


class MetaRobotsModule:
    """Module to analyze meta robots directives and detect issues"""
    
    def __init__(self, db: Database):
        """
        Initialize the Meta Robots module.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def analyze(self, scan_id: int, pages: List[Dict]) -> List[Dict]:
        """
        Analyze website for meta robots directives.
        
        Args:
            scan_id: Scan ID
            pages: List of pages from crawler
        
        Returns:
            List of meta robots issues found
        """
        issues = []
        
        for page in pages:
            if not page.get('html'):
                continue
                
            url = page['url']
            html = page['html']
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all meta robots tags
            meta_robots = soup.find_all('meta', attrs={'name': lambda x: x and x.lower() == 'robots'})
            
            if not meta_robots:
                # No meta robots tag found - this is usually OK but worth noting
                continue
            
            for meta in meta_robots:
                content = meta.get('content', '').strip().lower()
                
                if not content:
                    continue
                
                # Parse the directives
                directives = [d.strip() for d in content.split(',')]
                
                # Analyze each directive
                for directive in directives:
                    # Check for noindex
                    if directive == 'noindex':
                        issue = {
                            'issue_type': 'meta_robots_noindex',
                            'url': url,
                            'source_page': url,
                            'description': 'Page has meta robots noindex directive - will not be indexed by search engines',
                            'severity': 'high'
                        }
                        issues.append(issue)
                        self.db.add_issue(
                            scan_id=scan_id,
                            issue_type='meta_robots_noindex',
                            url=url,
                            source_page=url,
                            description=issue['description'],
                            severity='high'
                        )
                    
                    # Check for nofollow
                    elif directive == 'nofollow':
                        issue = {
                            'issue_type': 'meta_robots_nofollow',
                            'url': url,
                            'source_page': url,
                            'description': 'Page has meta robots nofollow directive - links will not be followed by search engines',
                            'severity': 'medium'
                        }
                        issues.append(issue)
                        self.db.add_issue(
                            scan_id=scan_id,
                            issue_type='meta_robots_nofollow',
                            url=url,
                            source_page=url,
                            description=issue['description'],
                            severity='medium'
                        )
                    
                    # Check for nosnippet
                    elif directive == 'nosnippet':
                        issue = {
                            'issue_type': 'meta_robots_nosnippet',
                            'url': url,
                            'source_page': url,
                            'description': 'Page has meta robots nosnippet directive - no snippet will be shown in search results',
                            'severity': 'medium'
                        }
                        issues.append(issue)
                        self.db.add_issue(
                            scan_id=scan_id,
                            issue_type='meta_robots_nosnippet',
                            url=url,
                            source_page=url,
                            description=issue['description'],
                            severity='medium'
                        )
                    
                    # Check for noarchive
                    elif directive == 'noarchive':
                        issue = {
                            'issue_type': 'meta_robots_noarchive',
                            'url': url,
                            'source_page': url,
                            'description': 'Page has meta robots noarchive directive - no cached copy will be stored',
                            'severity': 'info'
                        }
                        issues.append(issue)
                        self.db.add_issue(
                            scan_id=scan_id,
                            issue_type='meta_robots_noarchive',
                            url=url,
                            source_page=url,
                            description=issue['description'],
                            severity='info'
                        )
                    
                    # Check for notranslate
                    elif directive == 'notranslate':
                        issue = {
                            'issue_type': 'meta_robots_notranslate',
                            'url': url,
                            'source_page': url,
                            'description': 'Page has meta robots notranslate directive - no translation will be offered',
                            'severity': 'info'
                        }
                        issues.append(issue)
                        self.db.add_issue(
                            scan_id=scan_id,
                            issue_type='meta_robots_notranslate',
                            url=url,
                            source_page=url,
                            description=issue['description'],
                            severity='info'
                        )
                    
                    # Check for noimageindex
                    elif directive == 'noimageindex':
                        issue = {
                            'issue_type': 'meta_robots_noimageindex',
                            'url': url,
                            'source_page': url,
                            'description': 'Page has meta robots noimageindex directive - images will not be indexed',
                            'severity': 'medium'
                        }
                        issues.append(issue)
                        self.db.add_issue(
                            scan_id=scan_id,
                            issue_type='meta_robots_noimageindex',
                            url=url,
                            source_page=url,
                            description=issue['description'],
                            severity='medium'
                        )
                    
                    # Check for unavailable_after (with date)
                    elif directive.startswith('unavailable_after'):
                        issue = {
                            'issue_type': 'meta_robots_unavailable_after',
                            'url': url,
                            'source_page': url,
                            'description': f'Page has meta robots unavailable_after directive: {directive}',
                            'severity': 'info'
                        }
                        issues.append(issue)
                        self.db.add_issue(
                            scan_id=scan_id,
                            issue_type='meta_robots_unavailable_after',
                            url=url,
                            source_page=url,
                            description=issue['description'],
                            severity='info'
                        )
        
        return issues