# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
Report Translations Module

Provides bilingual (Spanish/English) translations for SEO reports.
"""

TRANSLATIONS = {
    'es': {
        'report_title': 'Informe SEO Profesional',
        'executive_summary': 'Resumen Ejecutivo',
        'seo_grade': 'Calificación SEO',
        'score': 'Puntuación',
        'analyzed_url': 'URL Analizada',
        'analysis_date': 'Fecha del Análisis',
        'total_pages': 'Páginas Analizadas',
        'total_issues': 'Problemas Totales',
        'high_priority': 'Prioridad Alta',
        'medium_priority': 'Prioridad Media',
        'low_priority': 'Prioridad Baja',
        'impact_on_google': 'Impacto en Google',
        'detailed_analysis': 'Análisis Detallado',
        'recommendations': 'Recomendaciones',
        'notes': 'Notas Adicionales',
        'description': 'Descripción',
        'priority': 'Prioridad',
        'examples': 'Ejemplos',
        'critical_issues': 'Problemas Críticos',
        'distribution': 'Distribución de Problemas',
        'next_steps': 'Próximos Pasos',
        'placeholder_client_name': '[Nombre del Cliente]',
        'placeholder_agency_contact': '[Información de Contacto de la Agencia]',
        'placeholder_notes': '[Agregar observaciones personalizadas aquí]',
        'placeholder_logo': '[Logo de la Agencia]',
        'call_to_action': 'Para asistencia profesional en la implementación de estas correcciones, contacte con nuestro equipo.',
        'grade_explanation': 'La calificación SEO se basa en el análisis de problemas técnicos que afectan el posicionamiento en Google.',
        'issues_by_severity': 'Problemas por Severidad',
        'must_correct': 'Debe corregirse inmediatamente',
        'should_correct': 'Debería corregirse pronto',
        'could_correct': 'Puede corregirse cuando sea posible',
        'executive_report': 'Informe Ejecutivo',
        'tool_tagline': 'Analizador SEO profesional',
        'issue_catalog': 'Catálogo Completo de Problemas',
        'catalog_note': 'A continuación se listan TODOS los problemas detectados, agrupados por categoría, sin ningún tipo de truncamiento.',
        'category': 'Categoría',
        'count': 'Nº',
        'url': 'URL',
        'source_page': 'Página de Origen',
        'severity': 'Severidad',
        'severity_high': 'Alta',
        'severity_medium': 'Media',
        'severity_low': 'Baja',
        'issues_label': 'problemas',
        'page': 'Página',
        'top_priority_issues': 'Problemas de Máxima Prioridad',
        'no_issues_found': 'No se encontraron problemas durante el análisis.',
        'full_listing': 'Listado completo ({count} problemas)',
    },
    'en': {
        'report_title': 'Professional SEO Report',
        'executive_summary': 'Executive Summary',
        'seo_grade': 'SEO Grade',
        'score': 'Score',
        'analyzed_url': 'Analyzed URL',
        'analysis_date': 'Analysis Date',
        'total_pages': 'Pages Analyzed',
        'total_issues': 'Total Issues',
        'high_priority': 'High Priority',
        'medium_priority': 'Medium Priority',
        'low_priority': 'Low Priority',
        'impact_on_google': 'Impact on Google',
        'detailed_analysis': 'Detailed Analysis',
        'recommendations': 'Recommendations',
        'notes': 'Additional Notes',
        'description': 'Description',
        'priority': 'Priority',
        'examples': 'Examples',
        'critical_issues': 'Critical Issues',
        'distribution': 'Issue Distribution',
        'next_steps': 'Next Steps',
        'placeholder_client_name': '[Client Name]',
        'placeholder_agency_contact': '[Agency Contact Information]',
        'placeholder_notes': '[Add personalized observations here]',
        'placeholder_logo': '[Agency Logo]',
        'call_to_action': 'For professional assistance in implementing these corrections, please contact our team.',
        'grade_explanation': 'The SEO grade is based on the analysis of technical issues affecting Google rankings.',
        'issues_by_severity': 'Issues by Severity',
        'must_correct': 'Must be corrected immediately',
        'should_correct': 'Should be corrected soon',
        'could_correct': 'Can be corrected when possible',
        'executive_report': 'Executive Report',
        'tool_tagline': 'Professional SEO analyzer',
        'issue_catalog': 'Complete Issue Catalog',
        'catalog_note': 'EVERY issue detected is listed below, grouped by category, with no truncation whatsoever.',
        'category': 'Category',
        'count': 'Count',
        'url': 'URL',
        'source_page': 'Source Page',
        'severity': 'Severity',
        'severity_high': 'High',
        'severity_medium': 'Medium',
        'severity_low': 'Low',
        'issues_label': 'issues',
        'page': 'Page',
        'top_priority_issues': 'Top High-Priority Issues',
        'no_issues_found': 'No issues were found during the analysis.',
        'full_listing': 'Full listing ({count} issues)',
    }
}

IMPACT_TEMPLATES = {
    'es': {
        'broken_links': {
            'impact': 'Los enlaces rotos deterioran la experiencia del usuario y dañan la autoridad del dominio. Google penaliza sitios con enlaces que retornan errores 404/500.',
            'priority_note': '⚠️ PRIORIDAD: ALTA\nLos enlaces rotos deben corregirse inmediatamente para evitar pérdida de tráfico y autoridad en Google.'
        },
        'broken_image': {
            'impact': 'Las imágenes rotas afectan la experiencia visual del usuario y pueden reducir el tiempo de permanencia en el sitio.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nLas imágenes rotas deben corregirse para mejorar la experiencia del usuario.'
        },
        'broken_script': {
            'impact': 'Los scripts rotos pueden interrumpir funcionalidades críticas del sitio, afectando la conversión y la experiencia del usuario.',
            'priority_note': '⚠️ PRIORIDAD: ALTA\nLos scripts rotos deben corregirse inmediatamente para restaurar funcionalidades.'
        },
        'broken_stylesheet': {
            'impact': 'Las hojas de estilo rotas afectan la apariencia visual del sitio, comprometiendo la imagen de marca.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nLas hojas de estilo rotas deben corregirse para mantener el diseño profesional.'
        },
        'missing_title': {
            'impact': 'Sin títulos optimizados, Google tiene dificultades para entender el contenido, afectando el CTR en resultados de búsqueda.',
            'priority_note': '⚠️ PRIORIDAD: ALTA\nLos títulos faltantes deben crearse inmediatamente.'
        },
        'missing_description': {
            'impact': 'Sin meta descriptions, Google usa contenido automático que suele ser menos efectivo para atraer clics.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nLas meta descriptions deben crearse para mejorar el CTR.'
        },
        'title_too_short': {
            'impact': 'Los títulos demasiado cortos no aprovechan el espacio disponible en resultados de búsqueda, perdiendo oportunidades de palabras clave.',
            'priority_note': '⚠️ PRIORIDAD: BAJA\nLos títulos deben ampliarse para incluir más información relevante.'
        },
        'title_too_long': {
            'impact': 'Los títulos demasiado largos son truncados en resultados de búsqueda, perdiendo información importante.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nLos títulos deben acortarse para evitar truncamiento.'
        },
        'meta_description_too_short': {
            'impact': 'Las meta descriptions cortas no proporcionan suficiente información para convencer a los usuarios de hacer clic.',
            'priority_note': '⚠️ PRIORIDAD: BAJA\nLas meta descriptions deben ampliarse para ser más persuasivas.'
        },
        'meta_description_too_long': {
            'impact': 'Las meta descriptions largas son truncadas, perdiendo el mensaje principal.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nLas meta descriptions deben acortarse para evitar truncamiento.'
        },
        'duplicate_title': {
            'impact': 'Los títulos duplicados causan confusión en Google sobre qué página mostrar, afectando el posicionamiento.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nLos títulos duplicados deben hacerse únicos para cada página.'
        },
        'duplicate_description': {
            'impact': 'Las meta descriptions duplicadas reducen la efectividad de cada página en resultados de búsqueda.',
            'priority_note': '⚠️ PRIORIDAD: BAJA\nLas meta descriptions duplicadas deben hacerse únicas.'
        },
        'missing_alt_tag': {
            'impact': 'Las imágenes sin alt text no son accesibles para usuarios con discapacidad visual y no ayudan al SEO de imágenes.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nTodas las imágenes deben tener alt text descriptivo.'
        },
        'missing_alt_text': {
            'impact': 'Las imágenes con alt text vacío no proporcionan información ni accesibilidad.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nLas imágenes con alt vacío deben tener descripciones.'
        },
        'short_alt_text': {
            'impact': 'Los alt text demasiado cortos no proporcionan suficiente contexto sobre la imagen.',
            'priority_note': '⚠️ PRIORIDAD: BAJA\nLos alt text deben ser más descriptivos.'
        },
        'missing_robots_txt': {
            'impact': 'Sin robots.txt, Google no tiene instrucciones claras sobre qué páginas rastrear, lo que puede afectar la indexación.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nDebe crearse un archivo robots.txt para guiar el rastreo.'
        },
        'missing_security_txt': {
            'impact': 'Sin security.txt, el sitio no demuestra compromiso con la seguridad, lo que puede afectar la confianza.',
            'priority_note': '⚠️ PRIORIDAD: BAJA\nDebe crearse un archivo security.txt para demostrar compromiso con seguridad.'
        },
        'missing_sitemap': {
            'impact': 'Sin sitemap.xml, Google puede perder páginas importantes, afectando la indexación completa del sitio.',
            'priority_note': '⚠️ PRIORIDAD: ALTA\nDebe crearse un sitemap.xml para asegurar indexación completa.'
        },
        'missing_llms_txt': {
            'impact': 'Sin llms.txt, el sitio no proporciona directrices para modelos de lenguaje, afectando la visibilidad en IA.',
            'priority_note': '⚠️ PRIORIDAD: BAJA\nDebe crearse un archivo llms.txt para optimizar visibilidad en IA.'
        },
        'missing_h1': {
            'impact': 'Sin H1, Google no tiene contexto claro sobre el tema principal de la página.',
            'priority_note': '⚠️ PRIORIDAD: ALTA\nTodas las páginas deben tener un H1 que describa el contenido principal.'
        },
        'multiple_h1_same_page': {
            'impact': 'Múltiples H1 en una página confunden a Google sobre la jerarquía del contenido.',
            'priority_note': '⚠️ PRIORIDAD: MEDIADebe haber solo un H1 por página.'
        },
        'duplicate_h1': {
            'impact': 'Los H1 duplicados causan competencia entre páginas para el mismo tema.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nLos H1 duplicados deben hacerse únicos.'
        },
        'invalid_header_hierarchy': {
            'impact': 'Una jerarquía de encabezados incorrecta dificulta que Google entienda la estructura del contenido.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nLa jerarquía de encabezados debe seguir el orden H1-H6.'
        },
        'hreflang_missing_self_reference': {
            'impact': 'Sin autorreferencia hreflang, Google puede tener dudas sobre la versión canónica de la página.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nDebe incluirse autorreferencia hreflang en todas las páginas multilingües.'
        },
        'hreflang_missing_x_default': {
            'impact': 'Sin x-default, Google no sabe qué versión mostrar a usuarios de idiomas no especificados.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nDebe incluirse x-default para sitios multilingües.'
        },
        'hreflang_duplicate_code': {
            'impact': 'Códigos hreflang duplicados causan confusión sobre qué versión de idioma usar.',
            'priority_note': '⚠️ PRIORIDAD: ALTA\nLos códigos hreflang duplicados deben eliminarse.'
        },
        'hreflang_invalid_code': {
            'impact': 'Códigos hreflang inválidos no son reconocidos por Google, afectando el SEO internacional.',
            'priority_note': '⚠️ PRIORIDAD: ALTA\nLos códigos hreflang deben usar formatos válidos (ISO 639-1).'
        },
        'hreflang_missing_return_link': {
            'impact': 'Sin enlaces de retorno, Google duda de la integridad de la estructura multilingüe.',
            'priority_note': '⚠️ PRIORIDAD: ALTA\nDebe haber enlaces de retorno entre todas las páginas multilingües.'
        },
        'hreflang_missing_canonical': {
            'impact': 'Sin canonical, Google puede indexar versiones incorrectas de páginas multilingües.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nDebe haber canonical en todas las páginas multilingües.'
        },
        'canonical_chain': {
            'impact': 'Las cadenas canonical diluyen la autoridad y confunden a Google sobre la página definitiva.',
            'priority_note': '⚠️ PRIORIDAD: ALTA\nLas cadenas canonical deben eliminarse; canonical debe apuntar directamente a la página definitiva.'
        },
        'canonical_to_404': {
            'impact': 'Canonical a páginas 404 desperdicia autoridad y confunde a Google.',
            'priority_note': '⚠️ PRIORIDAD: ALTA\nLos canonical deben apuntar a páginas existentes (200 OK).'
        },
        'canonical_to_redirect': {
            'impact': 'Canonical a redirecciones añade latencia y complica la estructura del sitio.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nLos canonical deben apuntar directamente a páginas, no a redirecciones.'
        },
        'canonical_url_variation': {
            'impact': 'Variaciones de URL en canonical pueden causar indexación duplicada.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nLos canonical deben usar URLs consistentes (con/sin www, con/sin trailing slash).'
        },
        'missing_canonical': {
            'impact': 'Sin canonical, Google puede indexar versiones duplicadas de la página.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nTodas las páginas deben tener un canonical.'
        },
        'orphan_page': {
            'impact': 'Las páginas huérfanas no son descubiertas por Google mediante rastreo, afectando su indexación.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nLas páginas huérfanas deben tener enlaces entrantes para ser descubiertas.'
        },
        'missing_json_ld': {
            'impact': 'Sin JSON-LD, Google tiene información limitada sobre el contenido estructurado.',
            'priority_note': '⚠️ PRIORIDAD: BAJA\nDebe implementarse JSON-LD para mejorar la comprensión del contenido.'
        },
        'json_ld_missing_type': {
            'impact': 'JSON-LD sin @type no es interpretado correctamente por Google.',
            'priority_note': '⚠️ PRIORIDAD: ALTA\nLos JSON-LD deben tener @type válido.'
        },
        'json_ld_unknown_type': {
            'impact': 'Tipos JSON-LD desconocidos no son reconocidos por Google.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nLos tipos JSON-LD deben usar esquemas válidos (schema.org).'
        },
        'json_ld_missing_properties': {
            'impact': 'JSON-LD sin propiedades requeridas no es efectivo para rich snippets.',
            'priority_note': '⚠️ PRIORIDAD: ALTA\nLos JSON-LD deben incluir todas las propiedades requeridas.'
        },
        'json_ld_short_headline': {
            'impact': 'Headlines demasiado cortos en JSON-LD no son efectivos para rich snippets.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nLos headlines en JSON-LD deben ser descriptivos.'
        },
        'json_ld_invalid_json': {
            'impact': 'JSON-LD inválido es ignorado completamente por Google.',
            'priority_note': '⚠️ PRIORIDAD: ALTA\nLos JSON-LD deben tener sintaxis JSON válida.'
        },
        'missing_microdata': {
            'impact': 'Sin microdata, Google tiene información limitada sobre el contenido estructurado.',
            'priority_note': '⚠️ PRIORIDAD: BAJA\nDebe considerarse implementar microdata para mejor comprensión.'
        },
        'microdata_missing_type': {
            'impact': 'Microdata sin itemscope/itemtype no es interpretado correctamente.',
            'priority_note': '⚠️ PRIORIDAD: ALTA\nEl microdata debe tener itemscope/itemtype válido.'
        },
        'microdata_unknown_type': {
            'impact': 'Tipos microdata desconocidos no son reconocidos por Google.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nLos tipos microdata deben usar esquemas válidos.'
        },
        'missing_rdfa': {
            'impact': 'Sin RDFa, Google tiene información limitada sobre el contenido estructurado.',
            'priority_note': '⚠️ PRIORIDAD: BAJA\nDebe considerarse implementar RDFa para mejor comprensión.'
        },
        'rdfa_unknown_type': {
            'impact': 'Tipos RDFa desconocidos no son reconocidos por Google.',
            'priority_note': '⚠️ PRIORIDAD: MEDIA\nLos tipos RDFa deben usar esquemas válidos.'
        },
        'thin_content': {
            'impact': 'El contenido delgado no proporciona valor a los usuarios y es penalizado por Google.',
            'priority_note': '⚠️ PRIORIDAD: ALTA\nEl contenido delgado debe expandirse con información valiosa.'
        },
    },
    'en': {
        'broken_links': {
            'impact': 'Broken links degrade user experience and damage domain authority. Google penalizes sites with returning 404/500 errors.',
            'priority_note': '⚠️ PRIORITY: HIGH\nBroken links must be corrected immediately to avoid traffic loss and authority damage.'
        },
        'broken_image': {
            'impact': 'Broken images affect visual user experience and can reduce time on site.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nBroken images must be corrected to improve user experience.'
        },
        'broken_script': {
            'impact': 'Broken scripts can interrupt critical site functionality, affecting conversion and user experience.',
            'priority_note': '⚠️ PRIORITY: HIGH\nBroken scripts must be corrected immediately to restore functionality.'
        },
        'broken_stylesheet': {
            'impact': 'Broken stylesheets affect the visual appearance of the site, compromising brand image.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nBroken stylesheets must be corrected to maintain professional design.'
        },
        'missing_title': {
            'impact': 'Without optimized titles, Google struggles to understand content, affecting CTR in search results.',
            'priority_note': '⚠️ PRIORITY: HIGH\nMissing titles must be created immediately.'
        },
        'missing_description': {
            'impact': 'Without meta descriptions, Google uses automated content which is usually less effective at attracting clicks.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nMeta descriptions must be created to improve CTR.'
        },
        'title_too_short': {
            'impact': 'Titles that are too short don\'t take advantage of available space in search results, losing keyword opportunities.',
            'priority_note': '⚠️ PRIORITY: LOW\nTitles should be expanded to include more relevant information.'
        },
        'title_too_long': {
            'impact': 'Titles that are too long are truncated in search results, losing important information.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nTitles should be shortened to avoid truncation.'
        },
        'meta_description_too_short': {
            'impact': 'Short meta descriptions don\'t provide enough information to convince users to click.',
            'priority_note': '⚠️ PRIORITY: LOW\nMeta descriptions should be expanded to be more persuasive.'
        },
        'meta_description_too_long': {
            'impact': 'Long meta descriptions are truncated, losing the main message.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nMeta descriptions should be shortened to avoid truncation.'
        },
        'duplicate_title': {
            'impact': 'Duplicate titles confuse Google about which page to display, affecting rankings.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nDuplicate titles must be made unique for each page.'
        },
        'duplicate_description': {
            'impact': 'Duplicate meta descriptions reduce the effectiveness of each page in search results.',
            'priority_note': '⚠️ PRIORITY: LOW\nDuplicate meta descriptions must be made unique.'
        },
        'missing_alt_tag': {
            'impact': 'Images without alt text are not accessible to visually impaired users and don\'t help image SEO.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nAll images must have descriptive alt text.'
        },
        'missing_alt_text': {
            'impact': 'Images with empty alt text provide no information or accessibility.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nImages with empty alt must have descriptions.'
        },
        'short_alt_text': {
            'impact': 'Alt text that is too short doesn\'t provide enough context about the image.',
            'priority_note': '⚠️ PRIORITY: LOW\nAlt text should be more descriptive.'
        },
        'missing_robots_txt': {
            'impact': 'Without robots.txt, Google doesn\'t have clear instructions about which pages to crawl, which can affect indexing.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nA robots.txt file must be created to guide crawling.'
        },
        'missing_security_txt': {
            'impact': 'Without security.txt, the site doesn\'t demonstrate commitment to security, which can affect trust.',
            'priority_note': '⚠️ PRIORITY: LOW\nA security.txt file must be created to demonstrate security commitment.'
        },
        'missing_sitemap': {
            'impact': 'Without sitemap.xml, Google may miss important pages, affecting complete site indexing.',
            'priority_note': '⚠️ PRIORITY: HIGH\nA sitemap.xml must be created to ensure complete indexing.'
        },
        'missing_llms_txt': {
            'impact': 'Without llms.txt, the site doesn\'t provide guidelines for language models, affecting AI visibility.',
            'priority_note': '⚠️ PRIORITY: LOW\nAn llms.txt file must be created to optimize AI visibility.'
        },
        'missing_h1': {
            'impact': 'Without H1, Google has no clear context about the main topic of the page.',
            'priority_note': '⚠️ PRIORITY: HIGH\nAll pages must have an H1 describing the main content.'
        },
        'multiple_h1_same_page': {
            'impact': 'Multiple H1s on a page confuse Google about the content hierarchy.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nThere should be only one H1 per page.'
        },
        'duplicate_h1': {
            'impact': 'Duplicate H1s cause competition between pages for the same topic.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nDuplicate H1s must be made unique.'
        },
        'invalid_header_hierarchy': {
            'impact': 'Incorrect header hierarchy makes it difficult for Google to understand content structure.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nHeader hierarchy should follow H1-H6 order.'
        },
        'hreflang_missing_self_reference': {
            'impact': 'Without hreflang self-reference, Google may have doubts about the canonical version of the page.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nHreflang self-reference must be included on all multilingual pages.'
        },
        'hreflang_missing_x_default': {
            'impact': 'Without x-default, Google doesn\'t know which version to show for unspecified language users.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nx-default must be included for multilingual sites.'
        },
        'hreflang_duplicate_code': {
            'impact': 'Duplicate hreflang codes cause confusion about which language version to use.',
            'priority_note': '⚠️ PRIORITY: HIGH\nDuplicate hreflang codes must be removed.'
        },
        'hreflang_invalid_code': {
            'impact': 'Invalid hreflang codes are not recognized by Google, affecting international SEO.',
            'priority_note': '⚠️ PRIORITY: HIGH\nHreflang codes must use valid formats (ISO 639-1).'
        },
        'hreflang_missing_return_link': {
            'impact': 'Without return links, Google doubts the integrity of the multilingual structure.',
            'priority_note': '⚠️ PRIORITY: HIGH\nReturn links must exist between all multilingual pages.'
        },
        'hreflang_missing_canonical': {
            'impact': 'Without canonical, Google may index incorrect versions of multilingual pages.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nCanonical must exist on all multilingual pages.'
        },
        'canonical_chain': {
            'impact': 'Canonical chains dilute authority and confuse Google about the definitive page.',
            'priority_note': '⚠️ PRIORITY: HIGH\nCanonical chains must be eliminated; canonical should point directly to the definitive page.'
        },
        'canonical_to_404': {
            'impact': 'Canonical to 404 pages wastes authority and confuses Google.',
            'priority_note': '⚠️ PRIORITY: HIGH\nCanonical must point to existing pages (200 OK).'
        },
        'canonical_to_redirect': {
            'impact': 'Canonical to redirects adds latency and complicates site structure.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nCanonical should point directly to pages, not redirects.'
        },
        'canonical_url_variation': {
            'impact': 'URL variations in canonical can cause duplicate indexing.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nCanonical should use consistent URLs (with/without www, with/without trailing slash).'
        },
        'missing_canonical': {
            'impact': 'Without canonical, Google may index duplicate versions of the page.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nAll pages must have a canonical.'
        },
        'orphan_page': {
            'impact': 'Orphan pages are not discovered by Google through crawling, affecting their indexing.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nOrphan pages must have incoming links to be discovered.'
        },
        'missing_json_ld': {
            'impact': 'Without JSON-LD, Google has limited information about structured content.',
            'priority_note': '⚠️ PRIORITY: LOW\nJSON-LD should be implemented to improve content understanding.'
        },
        'json_ld_missing_type': {
            'impact': 'JSON-LD without @type is not interpreted correctly by Google.',
            'priority_note': '⚠️ PRIORITY: HIGH\nJSON-LD must have valid @type.'
        },
        'json_ld_unknown_type': {
            'impact': 'Unknown JSON-LD types are not recognized by Google.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nJSON-LD types must use valid schemas (schema.org).'
        },
        'json_ld_missing_properties': {
            'impact': 'JSON-LD without required properties is not effective for rich snippets.',
            'priority_note': '⚠️ PRIORITY: HIGH\nJSON-LD must include all required properties.'
        },
        'json_ld_short_headline': {
            'impact': 'Headlines that are too short in JSON-LD are not effective for rich snippets.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nHeadlines in JSON-LD should be descriptive.'
        },
        'json_ld_invalid_json': {
            'impact': 'Invalid JSON-LD is completely ignored by Google.',
            'priority_note': '⚠️ PRIORITY: HIGH\nJSON-LD must have valid JSON syntax.'
        },
        'missing_microdata': {
            'impact': 'Without microdata, Google has limited information about structured content.',
            'priority_note': '⚠️ PRIORITY: LOW\nMicrodata should be considered for better content understanding.'
        },
        'microdata_missing_type': {
            'impact': 'Microdata without itemscope/itemtype is not interpreted correctly.',
            'priority_note': '⚠️ PRIORITY: HIGH\nMicrodata must have valid itemscope/itemtype.'
        },
        'microdata_unknown_type': {
            'impact': 'Unknown microdata types are not recognized by Google.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nMicrodata types must use valid schemas.'
        },
        'missing_rdfa': {
            'impact': 'Without RDFa, Google has limited information about structured content.',
            'priority_note': '⚠️ PRIORITY: LOW\nRDFa should be considered for better content understanding.'
        },
        'rdfa_unknown_type': {
            'impact': 'Unknown RDFa types are not recognized by Google.',
            'priority_note': '⚠️ PRIORITY: MEDIUM\nRDFa types must use valid schemas.'
        },
        'thin_content': {
            'impact': 'Thin content provides no value to users and is penalized by Google.',
            'priority_note': '⚠️ PRIORITY: HIGH\nThin content must be expanded with valuable information.'
        },
    }
}


def get_translation(lang: str, key: str) -> str:
    """
    Get a translation for a given language and key.
    
    Args:
        lang: Language code ('es' or 'en')
        key: Translation key
    
    Returns:
        Translated string or key if not found
    """
    if lang not in TRANSLATIONS:
        lang = 'en'
    
    return TRANSLATIONS[lang].get(key, key)


def get_impact_template(lang: str, issue_type: str) -> dict:
    """
    Get impact template for a given issue type.
    
    Args:
        lang: Language code ('es' or 'en')
        issue_type: Issue type (e.g., 'broken_links', 'missing_title')
    
    Returns:
        Dictionary with 'impact' and 'priority_note' keys
    """
    if lang not in IMPACT_TEMPLATES:
        lang = 'en'
    
    return IMPACT_TEMPLATES[lang].get(issue_type, {
        'impact': get_translation(lang, 'impact_on_google'),
        'priority_note': ''
    })

ISSUE_TYPE_LABELS = {
    'en': {
        'broken_link': 'Broken Link',
        'broken_image': 'Broken Image',
        'broken_script': 'Broken Script',
        'broken_stylesheet': 'Broken Stylesheet',
        'broken_resource': 'Broken Resource',
        'missing_title': 'Missing Title',
        'missing_description': 'Missing Meta Description',
        'duplicate_title': 'Duplicate Title',
        'duplicate_description': 'Duplicate Meta Description',
        'missing_alt_tag': 'Missing Image Alt Text',
        'missing_alt_text': 'Missing Image Alt Text',
        'short_alt_text': 'Short Image Alt Text',
        'missing_h1': 'Missing H1 Header',
        'multiple_h1_same_page': 'Multiple H1 Headers on the Same Page',
        'duplicate_h1': 'Duplicate H1 Header',
        'invalid_header_hierarchy': 'Invalid Header Hierarchy',
        'meta_robots_noindex': 'Meta Robots: noindex',
        'meta_robots_nofollow': 'Meta Robots: nofollow',
        'meta_robots_noarchive': 'Meta Robots: noarchive',
        'meta_robots_nosnippet': 'Meta Robots: nosnippet',
        'meta_robots_noimageindex': 'Meta Robots: noimageindex',
        'meta_robots_notranslate': 'Meta Robots: notranslate',
        'meta_robots_unavailable_after': 'Meta Robots: unavailable_after',
        'missing_robots_txt': 'Missing robots.txt',
        'missing_security_txt': 'Missing security.txt',
        'missing_sitemap': 'Missing sitemap.xml',
        'missing_llms_txt': 'Missing llms.txt',
        'robots_txt_found': 'robots.txt Found',
        'security_txt_found': 'security.txt Found',
        'sitemap_found': 'sitemap.xml Found',
        'llms_txt_found': 'llms.txt Found',
        'missing_canonical': 'Missing Canonical Tag',
        'canonical_chain': 'Canonical Chain',
        'canonical_to_404': 'Canonical Pointing to a 404 Page',
        'canonical_to_redirect': 'Canonical Pointing to a Redirect',
        'canonical_url_variation': 'Canonical URL Variation',
        'empty_canonical': 'Empty Canonical Tag',
        'hreflang_invalid_code': 'Invalid Hreflang Code',
        'hreflang_duplicate_code': 'Duplicate Hreflang Code',
        'hreflang_missing_self_reference': 'Hreflang Missing Self-Reference',
        'hreflang_missing_x_default': 'Hreflang Missing x-default',
        'hreflang_missing_return_link': 'Hreflang Missing Return Link',
        'hreflang_missing_canonical': 'Hreflang Without Canonical Tag',
        'orphan_page': 'Orphan Page',
        'missing_structured_data': 'Missing Structured Data',
        'json_ld_invalid_json': 'Invalid JSON-LD',
        'json_ld_missing_type': 'JSON-LD Missing Type',
        'json_ld_unknown_type': 'Unknown JSON-LD Type',
        'json_ld_missing_properties': 'JSON-LD Missing Properties',
        'json_ld_short_headline': 'JSON-LD Short Headline',
        'microdata_missing_type': 'Microdata Missing Type',
        'microdata_unknown_type': 'Unknown Microdata Type',
        'rdfa_unknown_type': 'Unknown RDFa Type',
        'title_too_long': 'Title Too Long',
        'title_too_short': 'Title Too Short',
        'meta_description_too_long': 'Meta Description Too Long',
        'meta_description_too_short': 'Meta Description Too Short',
        'thin_content': 'Thin Content',
    },
    'es': {
        'broken_link': 'Enlace roto',
        'broken_image': 'Imagen rota',
        'broken_script': 'Script roto',
        'broken_stylesheet': 'Hoja de estilos rota',
        'broken_resource': 'Recurso roto',
        'missing_title': 'Falta el título',
        'missing_description': 'Falta la meta descripción',
        'duplicate_title': 'Título duplicado',
        'duplicate_description': 'Meta descripción duplicada',
        'missing_alt_tag': 'Falta el texto alt de la imagen',
        'missing_alt_text': 'Falta el texto alt de la imagen',
        'short_alt_text': 'Texto alt demasiado corto',
        'missing_h1': 'Falta el encabezado H1',
        'multiple_h1_same_page': 'Varios encabezados H1 en la misma página',
        'duplicate_h1': 'Encabezado H1 duplicado',
        'invalid_header_hierarchy': 'Jerarquía de encabezados inválida',
        'meta_robots_noindex': 'Meta robots: noindex',
        'meta_robots_nofollow': 'Meta robots: nofollow',
        'meta_robots_noarchive': 'Meta robots: noarchive',
        'meta_robots_nosnippet': 'Meta robots: nosnippet',
        'meta_robots_noimageindex': 'Meta robots: noimageindex',
        'meta_robots_notranslate': 'Meta robots: notranslate',
        'meta_robots_unavailable_after': 'Meta robots: unavailable_after',
        'missing_robots_txt': 'Falta robots.txt',
        'missing_security_txt': 'Falta security.txt',
        'missing_sitemap': 'Falta sitemap.xml',
        'missing_llms_txt': 'Falta llms.txt',
        'robots_txt_found': 'robots.txt encontrado',
        'security_txt_found': 'security.txt encontrado',
        'sitemap_found': 'sitemap.xml encontrado',
        'llms_txt_found': 'llms.txt encontrado',
        'missing_canonical': 'Falta la etiqueta canónica',
        'canonical_chain': 'Cadena de canónicas',
        'canonical_to_404': 'Canónica que apunta a una página 404',
        'canonical_to_redirect': 'Canónica que apunta a una redirección',
        'canonical_url_variation': 'Variación de URL en la canónica',
        'empty_canonical': 'Etiqueta canónica vacía',
        'hreflang_invalid_code': 'Código hreflang inválido',
        'hreflang_duplicate_code': 'Código hreflang duplicado',
        'hreflang_missing_self_reference': 'Hreflang sin autorreferencia',
        'hreflang_missing_x_default': 'Hreflang sin x-default',
        'hreflang_missing_return_link': 'Hreflang sin enlace de retorno',
        'hreflang_missing_canonical': 'Hreflang sin etiqueta canónica',
        'orphan_page': 'Página huérfana',
        'missing_structured_data': 'Faltan datos estructurados',
        'json_ld_invalid_json': 'JSON-LD inválido',
        'json_ld_missing_type': 'JSON-LD sin tipo',
        'json_ld_unknown_type': 'Tipo de JSON-LD desconocido',
        'json_ld_missing_properties': 'JSON-LD con propiedades ausentes',
        'json_ld_short_headline': 'Titular de JSON-LD demasiado corto',
        'microdata_missing_type': 'Microdata sin tipo',
        'microdata_unknown_type': 'Tipo de microdata desconocido',
        'rdfa_unknown_type': 'Tipo de RDFa desconocido',
        'title_too_long': 'Título demasiado largo',
        'title_too_short': 'Título demasiado corto',
        'meta_description_too_long': 'Meta descripción demasiado larga',
        'meta_description_too_short': 'Meta descripción demasiado corta',
        'thin_content': 'Contenido insuficiente',
    },
}


def get_issue_label(lang: str, issue_type: str) -> str:
    """
    Get the human-readable label for an issue type.

    Args:
        lang: Language code ('es' or 'en')
        issue_type: Internal issue type (e.g., 'broken_link', 'missing_alt_tag')

    Returns:
        Translated label, or the raw issue type when no label exists
    """
    if lang not in ISSUE_TYPE_LABELS:
        lang = 'en'

    return ISSUE_TYPE_LABELS[lang].get(issue_type, issue_type)
