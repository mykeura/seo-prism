from bs4 import BeautifulSoup
from urllib.parse import urljoin


def analyze_h1_headers(soup: BeautifulSoup, url: str, all_pages_data: dict):
    """
    Analyzes H1 headers of a page and compares with other pages
    to detect duplicates.
    """
    issues = []
    
    # Get all H1 headers on the current page
    h1_elements = soup.find_all('h1')
    h1_texts = [h1.get_text(strip=True) for h1 in h1_elements if h1.get_text(strip=True)]
    
    if len(h1_elements) == 0:
        # No H1 on the page
        issues.append({
            'issue_type': 'missing_h1',
            'url': url,
            'source_page': url,
            'description': 'The page does not contain any H1 header',
            'severity': 'high'
        })
    elif len(h1_elements) > 1:
        # Multiple H1 on the same page
        issues.append({
            'issue_type': 'multiple_h1_same_page',
            'url': url,
            'source_page': url,
            'description': f'The page contains {len(h1_elements)} H1 headers',
            'severity': 'high'
        })
    else:
        # Only one H1 on the page, now check if it's duplicated on other pages
        current_h1 = h1_texts[0].lower() if h1_texts else ''
        
        # Search for duplicate H1 on other pages
        for other_url, page_data in all_pages_data.items():
            if other_url == url or not page_data.get('html'):
                continue
                
            try:
                other_soup = BeautifulSoup(page_data['html'], 'html.parser')
                other_h1_elements = other_soup.find_all('h1')
                other_h1_texts = [h1.get_text(strip=True).lower() for h1 in other_h1_elements if h1.get_text(strip=True)]
                
                if current_h1 in other_h1_texts:
                    issues.append({
                        'issue_type': 'duplicate_h1',
                        'url': url,
                        'source_page': url,
                        'description': f'Duplicate H1 found on another page: {other_url}',
                        'severity': 'high'
                    })
                    # Also report on the other page
                    issues.append({
                        'issue_type': 'duplicate_h1',
                        'url': other_url,
                        'source_page': other_url,
                        'description': f'Duplicate H1 found on another page: {url}',
                        'severity': 'high'
                    })
            except Exception as e:
                print(f"Error analyzing H1 on {other_url}: {str(e)}")
                continue
    
    return issues