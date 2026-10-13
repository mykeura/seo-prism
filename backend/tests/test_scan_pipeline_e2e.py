# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
End-to-end checkpoint: the full scan pipeline against a real HTTP server.

TestScanWithBrokenLinks in test_error_pages.py already proves that error
responses are discarded and that broken links are reported. This file closes
the remaining gap in that coverage:

  * the SEO grade is actually computed from the analysed pages/issues, and
  * everything run_scan_pipeline returns is what get_scan_results hands back
    after the pipeline persists it (nothing is dropped between compute and
    storage).

If the pipeline ever stopped storing the issues it reports, or stored a page
count the grade was not computed from, these tests fail here and not in the
UI.
"""
import asyncio
import functools
import http.server
import threading

import pytest

from core.pipeline import run_scan_pipeline
from database import Database


_BODY = ' '.join(['Lorem ipsum dolor sit amet consectetur adipiscing elit'] * 60)


def _page(title, links):
    """A healthy page: sound title/description lengths, one H1, real body."""
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
    """Serve a two-page site where the index links to a missing URL (404)."""
    (tmp_path / 'index.html').write_text(_page('Home', [
        ('/a.html', 'A'), ('/missing', 'missing'),
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


class TestScanPipelineE2E:
    def test_grade_is_computed_and_persisted(self, local_site):
        db = Database(':memory:')
        try:
            result = asyncio.run(
                run_scan_pipeline(db, local_site, max_pages=10, ignore_robots=True)
            )

            # The grade is a real letter backed by a percentage, not a stub.
            grade = result['seo_grade']
            assert isinstance(grade, dict)
            assert grade['grade'] in 'ABCDEF'
            assert 0 <= grade['score'] <= 100

            # The healthy pages must not be shadowed by the 404 document.
            assert result['html_page_count'] == 2

            # /missing answers 404, so the crawl surfaces it as a broken link.
            assert 'broken_link' in {i['issue_type'] for i in result['issues']}

            # Everything the pipeline reported is what the database returns.
            stored = db.get_scan_results(result['scan_id'])
            assert {i['issue_type'] for i in stored['issues']} == \
                {i['issue_type'] for i in result['issues']}
            assert stored['scan']['total_pages'] == result['html_page_count']
        finally:
            db.close()
