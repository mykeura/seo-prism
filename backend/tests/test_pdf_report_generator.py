# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
Unit tests for pdf_report_generator module.
"""
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from modules.pdf_report_generator import SEOReportPDFGenerator
from modules.description_translations import translate_description

pypdf = pytest.importorskip('pypdf', reason='pypdf needed to inspect generated PDFs')


def _make_issue(issue_id: int, issue_type: str, severity: str = 'medium') -> dict:
    return {
        'id': issue_id,
        'issue_type': issue_type,
        'url': f'https://example.com/page-{issue_id}',
        'source_page': 'https://example.com/home',
        'description': f'Demonstration issue on page {issue_id}',
        'severity': severity,
    }


@pytest.fixture
def sample_results():
    """Sample scan results for testing."""
    return {
        'scan': {
            'id': 1,
            'url': 'https://example.com',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_pages': 10,
            'total_issues': 25,
        },
        'issues': [
            _make_issue(1, 'broken_link', 'high'),
            _make_issue(2, 'broken_link', 'high'),
            _make_issue(3, 'missing_title', 'high'),
            _make_issue(4, 'missing_description', 'medium'),
            _make_issue(5, 'title_too_long', 'medium'),
            _make_issue(6, 'duplicate_title', 'medium'),
            _make_issue(7, 'missing_alt_tag', 'medium'),
            _make_issue(8, 'missing_h1', 'high'),
            _make_issue(9, 'invalid_header_hierarchy', 'medium'),
            _make_issue(10, 'thin_content', 'low'),
        ],
        'seo_grade': {
            'score': 68,
            'grade': 'C',
            'breakdown': {'high': 4, 'medium': 5, 'low': 1, 'total': 10},
        },
        'resource_analysis': {
            'html_pages': 10, 'css_files': 3, 'js_files': 5,
            'images': 12, 'other_resources': 2, 'total_resources': 32,
        },
    }


@pytest.fixture
def many_issues_results():
    """Results with one category holding 150 issues to force multi-page tables."""
    issues = [_make_issue(i, 'broken_link', 'high') for i in range(1, 151)]
    issues += [_make_issue(i, 'missing_alt_tag', 'medium') for i in range(151, 181)]
    return {
        'scan': {
            'id': 2,
            'url': 'https://example.com',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_pages': 60,
            'total_issues': len(issues),
        },
        'issues': issues,
        'seo_grade': {
            'score': 42,
            'grade': 'D',
            'breakdown': {'high': 150, 'medium': 30, 'low': 0, 'total': 180},
        },
        'resource_analysis': {},
    }


def _generate(tmp_path: str, results: dict, lang: str = 'en') -> tuple:
    output = str(Path(tmp_path) / 'seo_report.pdf')
    generator = SEOReportPDFGenerator()
    path = generator.generate_report(results, output, lang)
    return path, Path(path).read_bytes()


def _extract_text(pdf_path: str) -> str:
    reader = pypdf.PdfReader(pdf_path)
    return '\n'.join(page.extract_text() or '' for page in reader.pages)


class TestSEOReportPDFGenerator:

    def test_generates_valid_pdf(self, sample_results):
        with tempfile.TemporaryDirectory() as tmp_path:
            path, content = _generate(tmp_path, sample_results)
            assert os.path.exists(path)
            assert content.startswith(b'%PDF')
            assert len(content) > 5 * 1024

    def test_multilingual_generation(self, sample_results):
        with tempfile.TemporaryDirectory() as tmp_path:
            for lang in ('en', 'es'):
                path, content = _generate(tmp_path, sample_results, lang)
                assert os.path.exists(path)
                assert content.startswith(b'%PDF')

    def test_many_issues_spans_multiple_pages(self, many_issues_results):
        with tempfile.TemporaryDirectory() as tmp_path:
            path, _ = _generate(tmp_path, many_issues_results)
            reader = pypdf.PdfReader(path)
            assert len(reader.pages) > 3, (
                f'expected a multi-page catalog, got {len(reader.pages)} pages')

    def test_every_issue_url_is_present(self, many_issues_results):
        """Zero truncation: all 180 issue URLs must appear in the PDF text."""
        with tempfile.TemporaryDirectory() as tmp_path:
            path, _ = _generate(tmp_path, many_issues_results)
            text = _extract_text(path)
            missing = [
                issue['url'] for issue in many_issues_results['issues']
                if issue['url'] not in text
            ]
            assert not missing, f'{len(missing)} issue URLs missing from the PDF'

    def test_spanish_report_is_translated(self, sample_results):
        with tempfile.TemporaryDirectory() as tmp_path:
            path, _ = _generate(tmp_path, sample_results, lang='es')
            text = _extract_text(path)
            assert 'Resumen' in text
            assert 'Severidad' in text or 'severidad' in text.lower()

    def test_unwritable_path_raises(self, sample_results):
        generator = SEOReportPDFGenerator()
        with pytest.raises(Exception):
            generator.generate_report(
                sample_results, '/nonexistent-dir/seo_report.pdf', 'en')

    def test_issue_types_use_human_labels_es(self, sample_results):
        """Category codes must not leak into the Spanish report."""
        with tempfile.TemporaryDirectory() as tmp_path:
            path, _ = _generate(tmp_path, sample_results, lang='es')
            text = _extract_text(path)
            assert 'Enlace roto' in text
            assert 'Falta el título' in text
            assert 'Falta el texto alt de la imagen' in text  # missing_alt_tag label
            assert 'broken_link' not in text
            assert 'missing_title' not in text
            assert 'missing_alt_tag' not in text

    def test_issue_types_use_human_labels_en(self, sample_results):
        """Category codes must not leak into the English report."""
        with tempfile.TemporaryDirectory() as tmp_path:
            path, _ = _generate(tmp_path, sample_results, lang='en')
            text = _extract_text(path)
            assert 'Broken Link' in text
            assert 'Missing Title' in text
            assert 'broken_link' not in text
            assert 'missing_title' not in text

    def test_unknown_issue_type_falls_back_to_code(self):
        """Unmapped issue types still render (raw code as fallback)."""
        results = {
            'scan': {'id': 1, 'url': 'https://example.com', 'timestamp': '2026-08-23',
                     'total_pages': 1, 'total_issues': 1},
            'issues': [{
                'id': 1, 'issue_type': 'brand_new_check', 'url': 'https://example.com/x',
                'source_page': 'https://example.com/', 'description': 'future issue',
                'severity': 'low',
            }],
            'seo_grade': {}, 'resource_analysis': {},
        }
        with tempfile.TemporaryDirectory() as tmp_path:
            path, _ = _generate(tmp_path, results, lang='es')
            text = _extract_text(path)
            assert 'brand_new_check' in text


class TestTranslateDescription:

    def test_static_description_es(self):
        assert translate_description(
            'es', 'Missing or empty <title> tag') == 'Falta la etiqueta <title> o está vacía'
        assert translate_description(
            'es', 'robots.txt file not found - recommended for SEO') == \
            'Archivo robots.txt no encontrado - recomendado para SEO'

    def test_dynamic_description_es(self):
        assert translate_description(
            'es', 'Broken anchor (HTTP 404)') == 'Enlace roto (HTTP 404)'
        assert translate_description(
            'es', 'Broken image (HTTP 500)') == 'Imagen rota (HTTP 500)'
        assert translate_description(
            'es', 'The page contains 3 H1 headers') == 'La página contiene 3 encabezados H1'
        assert translate_description(
            'es', 'Duplicate H1 found on another page: https://example.com/a') == \
            'H1 duplicado encontrado en otra página: https://example.com/a'
        assert translate_description(
            'es', 'Title is too long (75 characters). Recommended: 10-60 characters') == \
            'El título es demasiado largo (75 caracteres). Recomendado: 10-60 caracteres'
        assert translate_description(
            'es', 'Page has thin content. Word count: 42 (minimum: 300), '
                  'Character count: 210 (minimum: 1000)') == \
            'La página tiene contenido insuficiente. Palabras: 42 (mínimo: 300), ' \
            'Caracteres: 210 (mínimo: 1000)'
        assert translate_description(
            'es', 'Invalid header hierarchy: H1 -> H4 (expected H2 or lower)') == \
            'Jerarquía de encabezados inválida: H1 -> H4 (se esperaba H2 o inferior)'

    def test_fallback_returns_original(self):
        assert translate_description('es', 'A brand new module message') == \
            'A brand new module message'
        assert translate_description('es', '') == ''
        assert translate_description('en', 'Missing or empty <title> tag') == \
            'Missing or empty <title> tag'

    def test_spanish_pdf_translates_descriptions(self):
        """The Descripción column of the Spanish report must be in Spanish."""
        results = {
            'scan': {'id': 1, 'url': 'https://example.com', 'timestamp': '2026-08-23',
                     'total_pages': 3, 'total_issues': 3},
            'issues': [
                {'id': 1, 'issue_type': 'missing_title', 'url': 'https://example.com/a',
                 'source_page': 'https://example.com/a',
                 'description': 'Missing or empty <title> tag', 'severity': 'high'},
                {'id': 2, 'issue_type': 'broken_link', 'url': 'https://example.com/x',
                 'source_page': 'https://example.com/a',
                 'description': 'Broken anchor (HTTP 404)', 'severity': 'high'},
                {'id': 3, 'issue_type': 'multiple_h1_same_page', 'url': 'https://example.com/b',
                 'source_page': 'https://example.com/b',
                 'description': 'The page contains 2 H1 headers', 'severity': 'high'},
            ],
            'seo_grade': {'score': 40, 'grade': 'D',
                          'breakdown': {'high': 3, 'medium': 0, 'low': 0, 'total': 3}},
            'resource_analysis': {},
        }
        with tempfile.TemporaryDirectory() as tmp_path:
            path, _ = _generate(tmp_path, results, lang='es')
            text = _extract_text(path)
            assert 'Falta la etiqueta <title> o está vacía' in text
            assert 'Enlace roto (HTTP 404)' in text
            assert 'La página contiene 2 encabezados H1' in text
            # English originals must not leak into the Spanish report
            assert 'Missing or empty' not in text
            assert 'Broken anchor' not in text
            assert 'The page contains' not in text
