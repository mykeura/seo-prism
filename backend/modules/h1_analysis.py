from bs4 import BeautifulSoup
from urllib.parse import urljoin


def analyze_h1_headers(soup: BeautifulSoup, url: str, all_pages_data: dict):
    """
    Analiza los encabezados H1 de una página y compara con otras páginas
    para detectar duplicados.
    """
    issues = []
    
    # Obtener todos los encabezados H1 en la página actual
    h1_elements = soup.find_all('h1')
    h1_texts = [h1.get_text(strip=True) for h1 in h1_elements if h1.get_text(strip=True)]
    
    if len(h1_elements) == 0:
        # No hay H1 en la página
        issues.append({
            'issue_type': 'missing_h1',
            'url': url,
            'source_page': url,
            'description': 'La página no contiene ningún encabezado H1',
            'severity': 'high'
        })
    elif len(h1_elements) > 1:
        # Hay múltiples H1 en la misma página
        issues.append({
            'issue_type': 'multiple_h1_same_page',
            'url': url,
            'source_page': url,
            'description': f'La página contiene {len(h1_elements)} encabezados H1',
            'severity': 'high'
        })
    else:
        # Solo hay un H1 en la página, ahora verificamos si está duplicado en otras páginas
        current_h1 = h1_texts[0].lower() if h1_texts else ''
        
        # Buscar H1 duplicados en otras páginas
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
                        'description': f'H1 duplicado encontrado en otra página: {other_url}',
                        'severity': 'high'
                    })
                    # También reportar en la otra página
                    issues.append({
                        'issue_type': 'duplicate_h1',
                        'url': other_url,
                        'source_page': other_url,
                        'description': f'H1 duplicado encontrado en otra página: {url}',
                        'severity': 'high'
                    })
            except Exception as e:
                print(f"Error analizando H1 en {other_url}: {str(e)}")
                continue
    
    return issues