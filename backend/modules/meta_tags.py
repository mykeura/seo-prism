# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

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
        
        h1_texts_by_url = {}
        h1_pages = {}
        h1_display = {}
        for page in crawled_pages:
            page_h1_texts = []
            try:
                page_soup = soup_for(page)
                if page_soup:
                    for h1 in page_soup.find_all('h1'):
                        text = h1.get_text(strip=True)
                        if not text:
                            continue
                        normalized = text.lower()
                        page_h1_texts.append(normalized)
                        h1_display.setdefault(normalized, text)
                        h1_pages.setdefault(normalized, []).append(page['url'])
            except Exception as e:
                print(f"Error extracting H1 on {page['url']}: {str(e)}")
            h1_texts_by_url[page['url']] = page_h1_texts
        
        for page in crawled_pages:
            page_url = page['url']
            html = page.get('html')
            
            if not html:
                continue
            
            soup = soup_for(page)
            
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
                
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='missing_title',
                    url=page_url,
                    source_page=page_url,
                    description='Missing or empty <title> tag',
                    severity='high'
                )
            
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
                
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='missing_description',
                    url=page_url,
                    source_page=page_url,
                    description='Missing or empty <meta name="description"> tag',
                    severity='medium'
                )
            
            h1_elements = soup.find_all('h1')
            
            if len(h1_elements) == 0:
                issue = {
                    'issue_type': 'missing_h1',
                    'url': page_url,
                    'source_page': page_url,
                    'description': 'The page does not contain any H1 header',
                    'severity': 'high'
                }
                issues.append(issue)
                
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='missing_h1',
                    url=page_url,
                    source_page=page_url,
                    description='The page does not contain any H1 header',
                    severity='high'
                )
            elif len(h1_elements) > 1:
                issue = {
                    'issue_type': 'multiple_h1_same_page',
                    'url': page_url,
                    'source_page': page_url,
                    'description': f'The page contains {len(h1_elements)} H1 headers',
                    'severity': 'high'
                }
                issues.append(issue)
                
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='multiple_h1_same_page',
                    url=page_url,
                    source_page=page_url,
                    description=f'The page contains {len(h1_elements)} H1 headers',
                    severity='high'
                )
            else:
                current_h1 = h1_texts_by_url.get(page_url, [''])[0]
                other_urls = list(dict.fromkeys(
                    url for url in h1_pages.get(current_h1, [])
                    if url != page_url
                ))
                
                if other_urls:
                    count = len(other_urls)
                    preview = ', '.join(other_urls[:3])
                    if count > 3:
                        preview += f' and {count - 3} more'
                    display = h1_display.get(current_h1, current_h1)
                    description = (
                        f'Duplicate H1 "{display}" found on {count} other '
                        f'page{"s" if count != 1 else ""}: {preview}'
                    )
                    issue = {
                        'issue_type': 'duplicate_h1',
                        'url': page_url,
                        'source_page': page_url,
                        'description': description,
                        'severity': 'high'
                    }
                    issues.append(issue)

                    self.db.add_issue(
                        scan_id=scan_id,
                        issue_type='duplicate_h1',
                        url=page_url,
                        source_page=page_url,
                        description=description,
                        severity='high'
                    )
            
            header_hierarchy_issues = analyze_header_hierarchy(soup, page_url)
            for issue in header_hierarchy_issues:
                issues.append(issue)
                
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type=issue['issue_type'],
                    url=issue['url'],
                    source_page=issue['source_page'],
                    description=issue['description'],
                    severity=issue['severity']
                )
        
        return issues