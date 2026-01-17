from bs4 import BeautifulSoup
import re


def analyze_header_hierarchy(soup: BeautifulSoup, url: str):
    """
    Analiza la jerarquía de encabezados en una página HTML.
    Verifica si los encabezados siguen una estructura lógica (H1 -> H2 -> H3, etc.)
    """
    issues = []
    
    # Encontrar todos los encabezados en orden
    headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    if not headers:
        return issues
    
    header_levels = []
    for header in headers:
        # Extraer el número del encabezado (h1 -> 1, h2 -> 2, etc.)
        level = int(re.search(r'h(\d)', header.name.lower()).group(1))
        header_levels.append(level)
    
    # Verificar jerarquía incorrecta
    for i in range(1, len(header_levels)):
        current_level = header_levels[i]
        previous_level = header_levels[i-1]
        
        # Si el salto de nivel es mayor a 1 (por ejemplo, de H1 a H3), es un error
        if current_level > previous_level + 1:
            issues.append({
                'issue_type': 'invalid_header_hierarchy',
                'url': url,
                'source_page': url,
                'description': f'Jerarquía inválida de encabezados: {previous_level} -> {current_level} (se esperaba H{previous_level+1} o menor)',
                'severity': 'medium'
            })
    
    # Opcional: verificar si hay saltos de nivel hacia atrás que podrían ser confusos
    # Por ejemplo: H1 -> H2 -> H4 -> H2 (el segundo H2 está bien, pero puede ser revisado)
    
    return issues