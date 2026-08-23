"""
Description translations for SEO reports.

The analysis modules generate issue descriptions in English (they are
hardcoded there). This module translates those descriptions to Spanish
for the reports without touching the analyzers: exact-match dictionary
first, then regex patterns for descriptions with interpolated values,
and the original text as fallback so an unknown description never
breaks report generation.

Usage:
    from modules.description_translations import translate_description
    texto = translate_description('es', issue['description'])
"""

import re

# Exact English descriptions emitted by the analysis modules -> Spanish.
STATIC_DESCRIPTIONS_ES = {
    'Missing or empty <title> tag':
        'Falta la etiqueta <title> o está vacía',
    'Missing or empty <meta name="description"> tag':
        'Falta la etiqueta <meta name="description"> o está vacía',
    'The page does not contain any H1 header':
        'La página no contiene ningún encabezado H1',
    'The page contains an H1 header with no text content':
        'La página contiene un encabezado H1 sin texto',
    'Image missing alt tag':
        'La imagen no tiene atributo alt',
    'Page has no incoming internal links':
        'La página no tiene enlaces internos entrantes',
    'Page is missing canonical tag':
        'Falta la etiqueta canónica en la página',
    'Canonical tag has empty href attribute':
        'La etiqueta canónica tiene el atributo href vacío',
    'No structured data found (JSON-LD, Microdata, or RDFa)':
        'No se encontraron datos estructurados (JSON-LD, Microdata o RDFa)',
    'JSON-LD schema missing @type property':
        'El esquema JSON-LD no tiene la propiedad @type',
    'Microdata element missing itemtype attribute':
        'El elemento Microdata no tiene el atributo itemtype',
    'Page does not reference itself with hreflang tag':
        'La página no se referencia a sí misma con la etiqueta hreflang',
    'Page has hreflang tags but missing canonical tag':
        'La página tiene etiquetas hreflang pero le falta la etiqueta canónica',
    'Missing x-default hreflang tag for non-language-specific version':
        'Falta la etiqueta hreflang x-default para la versión no específica de idioma',
    'Page has meta robots noindex directive - will not be indexed by search engines':
        'La página tiene la directiva meta robots noindex - no será indexada por los buscadores',
    'Page has meta robots nofollow directive - links will not be followed by search engines':
        'La página tiene la directiva meta robots nofollow - los enlaces no serán seguidos por los buscadores',
    'Page has meta robots noarchive directive - no cached copy will be stored':
        'La página tiene la directiva meta robots noarchive - no se almacenará copia en caché',
    'Page has meta robots nosnippet directive - no snippet will be shown in search results':
        'La página tiene la directiva meta robots nosnippet - no se mostrará fragmento en los resultados de búsqueda',
    'Page has meta robots noimageindex directive - images will not be indexed':
        'La página tiene la directiva meta robots noimageindex - las imágenes no serán indexadas',
    'Page has meta robots notranslate directive - no translation will be offered':
        'La página tiene la directiva meta robots notranslate - no se ofrecerá traducción',
    'robots.txt file found':
        'Archivo robots.txt encontrado',
    'robots.txt file not found - recommended for SEO':
        'Archivo robots.txt no encontrado - recomendado para SEO',
    'security.txt file found':
        'Archivo security.txt encontrado',
    'security.txt file not found - optional but recommended for security':
        'Archivo security.txt no encontrado - opcional pero recomendado por seguridad',
    'sitemap file found':
        'Archivo sitemap encontrado',
    'No sitemap found - highly recommended for SEO':
        'No se encontró sitemap - muy recomendado para SEO',
    'llms.txt file found - helps AI models understand your site':
        'Archivo llms.txt encontrado - ayuda a los modelos de IA a entender tu sitio',
    'llms.txt file not found - optional but recommended for AI discoverability':
        'Archivo llms.txt no encontrado - opcional pero recomendado para la descubribilidad por IA',
}

# Dynamic descriptions (f-strings in the analyzers): (pattern, template).
# The template placeholders {0}, {1}... receive the regex capture groups.
PATTERN_DESCRIPTIONS_ES = [
    (r'^Broken (?:anchor|link) \(HTTP (\d+)\)$', 'Enlace roto (HTTP {0})'),
    (r'^Broken image \(HTTP (\d+)\)$', 'Imagen rota (HTTP {0})'),
    (r'^Broken script \(HTTP (\d+)\)$', 'Script roto (HTTP {0})'),
    (r'^Broken stylesheet \(HTTP (\d+)\)$', 'Hoja de estilos rota (HTTP {0})'),
    (r'^Broken resource \(HTTP (\d+)\)$', 'Recurso roto (HTTP {0})'),
    (r'^The page contains (\d+) H1 headers$', 'La página contiene {0} encabezados H1'),
    (r'^Duplicate H1 found on another page: (.+)$', 'H1 duplicado encontrado en otra página: {0}'),
    (r'^Duplicate title found across (\d+) pages: "(.*)"$', 'Título duplicado en {0} páginas: "{1}"'),
    (r'^Duplicate meta description found across (\d+) pages: "(.*)"$', 'Meta descripción duplicada en {0} páginas: "{1}"'),
    (r'^Image without alt attribute: (.+)$', 'Imagen sin atributo alt: {0}'),
    (r'^Image with very short alt text: (.+) \(alt: "(.*)"\)$', 'Imagen con texto alt muy corto: {0} (alt: "{1}")'),
    (r'^Invalid header hierarchy: H(\d+) -> H(\d+) \(expected H(\d+) or lower\)$',
     'Jerarquía de encabezados inválida: H{0} -> H{1} (se esperaba H{2} o inferior)'),
    (r'^Title is too long \((\d+) characters\)\. Recommended: (\d+)-(\d+) characters$',
     'El título es demasiado largo ({0} caracteres). Recomendado: {1}-{2} caracteres'),
    (r'^Title is too short \((\d+) characters\)\. Recommended: (\d+)-(\d+) characters$',
     'El título es demasiado corto ({0} caracteres). Recomendado: {1}-{2} caracteres'),
    (r'^Meta description is too long \((\d+) characters\)\. Recommended: (\d+)-(\d+) characters$',
     'La meta descripción es demasiado larga ({0} caracteres). Recomendado: {1}-{2} caracteres'),
    (r'^Meta description is too short \((\d+) characters\)\. Recommended: (\d+)-(\d+) characters$',
     'La meta descripción es demasiado corta ({0} caracteres). Recomendado: {1}-{2} caracteres'),
    (r'^Canonical points to non-existent page \((\d+)\): (.+)$',
     'La canónica apunta a una página inexistente ({0}): {1}'),
    (r'^Canonical points to redirected page \((\d+)\): (.+)$',
     'La canónica apunta a una página redirigida ({0}): {1}'),
    (r'^Canonical points to URL with (.+): (.+)$', 'La canónica apunta a una URL con {0}: {1}'),
    (r'^Circular canonical chain detected: (.+) → (.+) → (.+)$',
     'Cadena canónica circular detectada: {0} → {1} → {2}'),
    (r'^Excessive canonical chain detected: (.+)$', 'Cadena de canónicas excesiva detectada: {0}'),
    (r'^Invalid hreflang code "(.+)" found$', 'Código hreflang inválido: "{0}"'),
    (r'^Duplicate hreflang code "(.+?)" found\. First: (.*), Second: (.*)$',
     'Código hreflang duplicado "{0}" encontrado. Primero: {1}, Segundo: {2}'),
    (r'^Missing return link: (\S+) does not reference back to (\S+) with hreflang="(.+)"$',
     'Falta el enlace de retorno: {0} no referencia de vuelta a {1} con hreflang="{2}"'),
    (r'^Page has meta robots unavailable_after directive: (.+)$',
     'La página tiene la directiva meta robots unavailable_after: {0}'),
    (r'^Page has thin content\. Word count: (\d+) \(minimum: (\d+)\), Character count: (\d+) \(minimum: (\d+)\)$',
     'La página tiene contenido insuficiente. Palabras: {0} (mínimo: {1}), Caracteres: {2} (mínimo: {3})'),
    (r'^Unknown schema type: (.+)$', 'Tipo de esquema desconocido: {0}'),
    (r'^Unknown microdata type: (.+)$', 'Tipo de microdata desconocido: {0}'),
    (r'^Unknown RDFa type: (.+)$', 'Tipo de RDFa desconocido: {0}'),
    (r'^Article headline too short \(< 10 characters\): (.+)$',
     'Titular del artículo demasiado corto (< 10 caracteres): {0}'),
    (r'^Schema (.+) missing required properties: (.+)$',
     'El esquema {0} tiene propiedades requeridas ausentes: {1}'),
    (r'^Invalid JSON-LD syntax: (.+)$', 'Sintaxis JSON-LD inválida: {0}'),
]

_COMPILED_PATTERNS = [(re.compile(pattern), template)
                      for pattern, template in PATTERN_DESCRIPTIONS_ES]


def translate_description(lang: str, description: str) -> str:
    """
    Translate an issue description to the report language.

    Args:
        lang: Language code ('es' or 'en'); descriptions are generated in
              English, so any other language code returns the original text
        description: Original description from the analysis modules

    Returns:
        Translated description, or the original text when there is no
        translation available (never fails)
    """
    if lang != 'es' or not description:
        return description

    exact = STATIC_DESCRIPTIONS_ES.get(description)
    if exact:
        return exact

    for pattern, template in _COMPILED_PATTERNS:
        match = pattern.match(description)
        if match:
            return template.format(*match.groups())

    return description
