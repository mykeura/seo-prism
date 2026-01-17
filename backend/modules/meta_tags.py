from typing import List, Dict
from bs4 import BeautifulSoup
from database import Database
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from header_hierarchy import analyze_header_hierarchy


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
        
        # Preparar datos para análisis de H1 entre páginas
        all_pages_data = {}
        for page in crawled_pages:
            all_pages_data[page['url']] = {'html': page.get('html', '')}
        
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
                # No hay H1 en la página
                issue = {
                    'issue_type': 'missing_h1',
                    'url': page_url,
                    'source_page': page_url,
                    'description': 'La página no contiene ningún encabezado H1',
                    'severity': 'high'
                }
                issues.append(issue)
                
                # Add to database
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='missing_h1',
                    url=page_url,
                    source_page=page_url,
                    description='La página no contiene ningún encabezado H1',
                    severity='high'
                )
            elif len(h1_elements) > 1:
                # Hay múltiples H1 en la misma página
                issue = {
                    'issue_type': 'multiple_h1_same_page',
                    'url': page_url,
                    'source_page': page_url,
                    'description': f'La página contiene {len(h1_elements)} encabezados H1',
                    'severity': 'high'
                }
                issues.append(issue)
                
                # Add to database
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='multiple_h1_same_page',
                    url=page_url,
                    source_page=page_url,
                    description=f'La página contiene {len(h1_elements)} encabezados H1',
                    severity='high'
                )
            else:
                # Solo hay un H1 en la página, ahora verificamos si está duplicado en otras páginas
                current_h1 = h1_texts[0].lower() if h1_texts else ''
                
                # Buscar H1 duplicados en otras páginas
                for other_url, page_data in all_pages_data.items():
                    if other_url == page_url or not page_data.get('html'):
                        continue
                        
                    try:
                        other_soup = BeautifulSoup(page_data['html'], 'html.parser')
                        other_h1_elements = other_soup.find_all('h1')
                        other_h1_texts = [h1.get_text(strip=True).lower() for h1 in other_h1_elements if h1.get_text(strip=True)]
                        
                        if current_h1 in other_h1_texts:
                            issue = {
                                'issue_type': 'duplicate_h1',
                                'url': page_url,
                                'source_page': page_url,
                                'description': f'H1 duplicado encontrado en otra página: {other_url}',
                                'severity': 'high'
                            }
                            issues.append(issue)
                            
                            # Add to database
                            self.db.add_issue(
                                scan_id=scan_id,
                                issue_type='duplicate_h1',
                                url=page_url,
                                source_page=page_url,
                                description=f'H1 duplicado encontrado en otra página: {other_url}',
                                severity='high'
                            )
                    except Exception as e:
                        print(f"Error analizando H1 en {other_url}: {str(e)}")
                        continue
            
            # Analizar jerarquía de encabezados
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