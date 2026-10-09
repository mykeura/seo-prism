# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
Regression tests: error responses (404, 5xx...) must not be treated as pages.

Historic bug: servers answer a missing URL with an HTML error document. The
crawler stored it like any other page, so it was counted in the page total
that the SEO grade divides by and analysed by every module (short title,
missing description, thin content, duplicated H1...). One broken link
therefore produced a cascade of bogus issues and dragged the grade down.
"""
import asyncio
import functools
import http.server
import threading

import pytest

from core.pipeline import (
    discard_error_page_content,
    is_error_response,
    run_scan_pipeline,
)
from modules.resource_analyzer import ResourceAnalyzer
from modules.seo_grade import SEOGradeCalculator


class TestIsErrorResponse:
    @pytest.mark.parametrize('status', [200, 204, 301, 302, 399])
    def test_success_and_redirects_are_pages(self, status):
        assert is_error_response({'status': status}) is False

    @pytest.mark.parametrize('status', [0, 400, 403, 404, 408, 410, 500, 503])
    def test_errors_are_not_pages(self, status):
        assert is_error_response({'status': status}) is True

    def test_missing_status_is_not_a_page(self):
        assert is_error_response({}) is True


class TestDiscardErrorPageContent:
    def _pages(self):
        return [
            {'url': 'http://x.test/', 'status': 200, 'html': '<html>ok</html>',
             'links': ['http://x.test/a'], 'resources': [{'url': 'u', 'type': 'anchor'}]},
            {'url': 'http://x.test/gone', 'status': 404, 'html': '<html>Not found</html>',
             'links': ['http://x.test/'], 'resources': [{'url': 'v', 'type': 'image'}]},
            {'url': 'http://x.test/boom', 'status': 500, 'html': '<html>Oops</html>',
             'links': [], 'resources': []},
        ]

    def test_error_pages_lose_their_content(self):
        pages = self._pages()
        discard_error_page_content(pages)

        for page in pages[1:]:
            assert page['html'] is None
            assert page['links'] == []
            assert page['resources'] == []

    def test_error_pages_keep_url_and_status(self):
        """Broken-link and canonical checks read the status of these entries."""
        pages = self._pages()
        discard_error_page_content(pages)

        assert (pages[1]['url'], pages[1]['status']) == ('http://x.test/gone', 404)
        assert (pages[2]['url'], pages[2]['status']) == ('http://x.test/boom', 500)

    def test_healthy_pages_are_untouched(self):
        pages = self._pages()
        discard_error_page_content(pages)

        assert pages[0]['html'] == '<html>ok</html>'
        assert pages[0]['links'] == ['http://x.test/a']
        assert len(pages[0]['resources']) == 1


class TestResourceAnalyzerIgnoresErrorPages:
    def test_404_html_body_is_not_an_html_page(self):
        analysis = ResourceAnalyzer().analyze_resources([
            {'url': 'http://x.test/', 'status': 200, 'html': '<html>ok</html>'},
            {'url': 'http://x.test/gone', 'status': 404, 'html': '<html>Not found</html>'},
        ])

        assert analysis['html_pages'] == 1
        assert analysis['other_resources'] == 1
        assert analysis['total_resources'] == 2

    def test_failed_page_with_html_extension_is_not_an_html_page(self):
        analysis = ResourceAnalyzer().analyze_resources([
            {'url': 'http://x.test/', 'status': 200, 'html': '<html>ok</html>'},
            {'url': 'http://x.test/old.html', 'status': 404, 'html': None},
            {'url': 'http://x.test/slow.php', 'status': 408, 'html': None},
            {'url': 'http://x.test/down.aspx', 'status': 0, 'html': None},
        ])

        assert analysis['html_pages'] == 1
        assert analysis['other_resources'] == 3


class TestGradeRobustness:
    def test_none_severity_does_not_crash(self):
        result = SEOGradeCalculator().calculate_grade(
            10, [{'severity': None}, {'severity': 'high'}]
        )
        assert 0 <= result['score'] <= 100

    def test_missing_severity_key_counts_as_medium(self):
        calc = SEOGradeCalculator()
        assert (calc.calculate_grade(10, [{}])['score']
                == calc.calculate_grade(10, [{'severity': 'medium'}])['score'])


# ---------------------------------------------------------------------------
# End to end: a real scan against a local HTTP server
# ---------------------------------------------------------------------------

_BODY = ' '.join(['Lorem ipsum dolor sit amet consectetur adipiscing elit'] * 60)


def _page(title, links):
    anchors = ' '.join(f'<a href="{href}">{label}</a>' for href, label in links)
    return (
        '<!doctype html><html lang="en"><head>'
        f'<title>{title} - a title with a healthy length for search results</title>'
        '<meta name="description" content="A description that is long enough to sit '
        'comfortably inside the recommended range for search result snippets.">'
        f'</head><body><h1>{title}</h1><p>{_BODY}</p>{anchors}</body></html>'
    )


@pytest.fixture
def local_site(tmp_path):
    (tmp_path / 'index.html').write_text(_page('Home', [
        ('/a.html', 'A'), ('/missing1.html', 'm1'), ('/missing2.html', 'm2'),
        ('/missing3.html', 'm3'),
    ]))
    (tmp_path / 'a.html').write_text(_page('Page A', [('/', 'home')]))

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    handler = functools.partial(QuietHandler, directory=str(tmp_path))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_address[1]}/'
    finally:
        server.shutdown()
        server.server_close()


class TestScanWithBrokenLinks:
    def test_error_pages_are_not_counted_nor_analysed(self, temp_db, local_site):
        result = asyncio.run(run_scan_pipeline(temp_db, local_site, 50, True))

        # Only the two real pages count; the three 404 documents do not.
        assert result['html_page_count'] == 2

        # The missing URLs are reported as broken links and nothing else.
        for n in (1, 2, 3):
            kinds = {i['issue_type'] for i in result['issues']
                     if f'missing{n}.html' in i['url']}
            assert kinds == {'broken_link'}, f'missing{n}.html -> {kinds}'

    def test_broken_links_are_still_detected(self, temp_db, local_site):
        result = asyncio.run(run_scan_pipeline(temp_db, local_site, 50, True))

        broken = [i for i in result['issues'] if i['issue_type'] == 'broken_link']
        assert len(broken) == 3

    def test_stored_scan_total_matches_the_graded_page_count(self, temp_db, local_site):
        result = asyncio.run(run_scan_pipeline(temp_db, local_site, 50, True))

        stored = temp_db.get_scan_results(result['scan_id'])
        assert stored['scan']['total_pages'] == result['html_page_count'] == 2
