from typing import List, Dict
from core.soup import soup_for
from database import Database
from modules.header_hierarchy import analyze_header_hierarchy


class MetaTagsModule:
    """Module to validate meta tags in crawled pages - focused on missing tags only."""
    
    def __init__(self, db: Database):
        """
        Initialize the Meta Tags module.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def analyze(self, scan_id: int, crawled_pages: List[Dict]) -> List[Dict]:
        """
        Analyze crawled pages for missing meta tags only (not duplicates).
        
        Args:
            scan_id: Scan ID
            crawled_pages: List of crawled page results
        
        Returns:
            List of meta tag issues
        """
        issues = []
        
        # Prepare data for H1 analysis between pages
        all_pages_data = {}
        for page in crawled_pages:
            all_pages_data[page['url']] = {'html': page.get('html', '')}
        
        for page in crawled_pages:
            page_url = page['url']
            html = page.get('html')
            
            if not html:
                continue
            
            soup = soup_for(page)
            
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
            
            # Check for H1 tags
            h1_elements = soup.find_all('h1')
            h1_texts = [h1.get_text(strip=True) for h1 in h1_elements if h1.get_text(strip=True)]
            
            if len(h1_elements) == 0:
                # No H1 on the page
                issue = {
                    'issue_type': 'missing_h1',
                    'url': page_url,
                    'source_page': page_url,
                    'description': 'The page does not contain any H1 header',
                    'severity': 'high'
                }
                issues.append(issue)
                
                # Add to database
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='missing_h1',
                    url=page_url,
                    source_page=page_url,
                    description='The page does not contain any H1 header',
                    severity='high'
                )
            elif len(h1_elements) > 1:
                # Multiple H1 on the same page
                issue = {
                    'issue_type': 'multiple_h1_same_page',
                    'url': page_url,
                    'source_page': page_url,
                    'description': f'The page contains {len(h1_elements)} H1 headers',
                    'severity': 'high'
                }
                issues.append(issue)
                
                # Add to database
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='multiple_h1_same_page',
                    url=page_url,
                    source_page=page_url,
                    description=f'The page contains {len(h1_elements)} H1 headers',
                    severity='high'
                )
            else:
                # Only one H1 on the page, now check if it's duplicated on other pages
                current_h1 = h1_texts[0].lower() if h1_texts else ''
                
                # Search for duplicate H1 on other pages
                for other_url, page_data in all_pages_data.items():
                    if other_url == page_url or not page_data.get('html'):
                        continue
                        
                    try:
                        other_soup = soup_for(page_data)
                        other_h1_elements = other_soup.find_all('h1')
                        other_h1_texts = [h1.get_text(strip=True).lower() for h1 in other_h1_elements if h1.get_text(strip=True)]
                        
                        if current_h1 in other_h1_texts:
                            issue = {
                                'issue_type': 'duplicate_h1',
                                'url': page_url,
                                'source_page': page_url,
                                'description': f'Duplicate H1 found on another page: {other_url}',
                                'severity': 'high'
                            }
                            issues.append(issue)
                            
                            # Add to database
                            self.db.add_issue(
                                scan_id=scan_id,
                                issue_type='duplicate_h1',
                                url=page_url,
                                source_page=page_url,
                                description=f'Duplicate H1 found on another page: {other_url}',
                                severity='high'
                            )
                    except Exception as e:
                        print(f"Error analyzing H1 on {other_url}: {str(e)}")
                        continue
            
            # Analyze header hierarchy
            header_hierarchy_issues = analyze_header_hierarchy(soup, page_url)
            for issue in header_hierarchy_issues:
                issues.append(issue)
                
                # Add to database
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type=issue['issue_type'],
                    url=issue['url'],
                    source_page=issue['source_page'],
                    description=issue['description'],
                    severity=issue['severity']
                )
        
        return issues