# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""Redirect handling: final URL, relative links and cross-host policy.

Historic bug: the crawler followed redirects but stored the requested URL and
resolved relative links against it, so /target/relative.html became
/relative.html, the 301/302 status disappeared, and canonical_to_redirect
could never fire.
"""
import asyncio
import http.server
import threading

import pytest

from core.crawler import Crawler
from core.pipeline import run_scan_pipeline
from database import Database
from modules.broken_links import BrokenLinksModule
from modules.canonical_tags import CanonicalTagsModule
from modules.resource_analyzer import ResourceAnalyzer


class _RouteHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        self._respond(send_body=True)

    def do_HEAD(self):
        self._respond(send_body=False)

    def _respond(self, send_body):
        path = self.path.split('?', 1)[0]
        self.server.requests.append((self.command, path))
        route = self.server.routes.get(path)
        if route is None:
            body = '<html><head><title>Not found</title></head><body>404</body></html>'
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            if send_body:
                self.wfile.write(body.encode())
            return

        status, headers, body = route
        self.send_response(status)
        for name, value in headers.items():
            self.send_header(name, value)
        if body is not None:
            self.send_header('Content-Length', str(len(body.encode())))
        self.end_headers()
        if send_body and body:
            self.wfile.write(body.encode())


class _Site:
    def __init__(self, routes):
        self.server = http.server.ThreadingHTTPServer(
            ('127.0.0.1', 0), _RouteHandler)
        self.server.routes = routes
        self.server.requests = []
        self.thread = threading.Thread(
            target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.server.server_address[1]}'

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def _html(title, body=''):
    return (
        f'<!doctype html><html><head><title>{title}</title></head>'
        f'<body><h1>{title}</h1>{body}</body></html>'
    )


def _page(title, links=()):
    anchors = ''.join(f'<a href="{href}">{label}</a>' for href, label in links)
    return (200, {'Content-Type': 'text/html; charset=utf-8'},
            _html(title, anchors))


def _redirect(location, status=302):
    return (status, {'Location': location}, None)


async def _crawl(base):
    async with Crawler(base, ignore_robots=True) as crawler:
        return await crawler.crawl(max_pages=10)


def _by_url(results):
    return {result['url']: result for result in results}


def test_redirect_metadata_and_relative_links_use_the_final_url():
    site = _Site({
        '/': _page('Home', [('/r', 'redirect')]),
        '/r': _redirect('/target/'),
        '/target/': _page('Target', [('relative.html', 'relative')]),
        '/target/relative.html': _page('Relative'),
    })
    try:
        results = asyncio.run(_crawl(site.base))
    finally:
        site.close()

    pages = _by_url(results)
    target = pages[f'{site.base}/target']

    assert target['status'] == 200
    assert target['requested_url'] == f'{site.base}/r'
    assert target['redirect_status'] == 302
    assert target['final_status'] == 200
    assert target['final_url'] == f'{site.base}/target'
    assert target['redirect_chain'] == [f'{site.base}/r', f'{site.base}/target']

    # The relative anchor resolves against /target/, not against /r.
    assert f'{site.base}/target/relative.html' in pages
    assert f'{site.base}/relative.html' not in pages
    assert target['links'] == [f'{site.base}/target/relative.html']

    # Redirect hops are not counted as HTML pages.
    analysis = ResourceAnalyzer().analyze_resources(results)
    assert analysis['html_pages'] == 3


def test_same_site_redirect_to_an_already_visited_url_is_a_redirect_hop():
    site = _Site({
        '/': _page('Home', [('/target', 'target'), ('/r', 'redirect')]),
        '/target': _page('Target'),
        '/r': _redirect('/target'),
    })
    try:
        results = asyncio.run(_crawl(site.base))
    finally:
        site.close()

    pages = _by_url(results)
    assert pages[f'{site.base}/target']['html']
    # Whichever URL was fetched first, /r must never become a second copy of
    # the target page; it is recorded as a redirect-only hop.
    redirect_hop = pages.get(f'{site.base}/r')
    if redirect_hop is not None:
        assert redirect_hop['is_redirect'] is True
        assert redirect_hop['html'] is None
        assert redirect_hop['final_url'] == f'{site.base}/target'


def test_cross_host_redirect_is_recorded_but_not_analysed():
    external = _Site({
        '/landing': _page('External site'),
    })
    site = _Site({
        '/': _page('Home', [('/away', 'away')]),
        '/away': _redirect(f'{external.base}/landing'),
    })
    try:
        results = asyncio.run(_crawl(site.base))
    finally:
        site.close()
        external.close()

    pages = _by_url(results)
    hop = pages[f'{site.base}/away']

    assert hop['is_redirect'] is True
    assert hop['status'] == 302
    assert hop['final_status'] == 200
    assert hop['final_url'] == f'{external.base}/landing'
    assert hop['html'] is None
    assert f'{external.base}/landing' not in pages

    analysis = ResourceAnalyzer().analyze_resources(results)
    assert analysis['html_pages'] == 1


def test_root_redirect_adopts_the_final_origin_for_crawling():
    destination = _Site({
        '/landing/': _page('Landing', [('child.html', 'child')]),
        '/landing/child.html': _page('Child'),
    })
    origin = _Site({
        '/': _redirect(f'{destination.base}/landing/'),
    })
    try:
        results = asyncio.run(_crawl(origin.base))
    finally:
        origin.close()
        destination.close()

    pages = _by_url(results)
    landing_url = f'{destination.base}/landing'
    child_url = f'{destination.base}/landing/child.html'

    assert landing_url in pages
    assert child_url in pages
    assert pages[landing_url]['requested_url'] == origin.base
    assert pages[landing_url]['redirect_status'] == 302
    assert pages[landing_url]['html']


def test_canonical_to_a_real_redirect_is_detected():
    home_html = (
        '<!doctype html><html><head><title>Home</title>'
        '<link rel="canonical" href="/r"></head>'
        '<body><h1>Home</h1><a href="/r">redirect</a></body></html>'
    )
    site = _Site({
        '/': (200, {'Content-Type': 'text/html; charset=utf-8'}, home_html),
        '/r': _redirect('/target/'),
        '/target/': _page('Target'),
    })
    try:
        results = asyncio.run(_crawl(site.base))
    finally:
        site.close()

    issues = CanonicalTagsModule(None).analyze(1, results)

    redirect_issues = [i for i in issues if i['issue_type'] == 'canonical_to_redirect']
    assert len(redirect_issues) == 1
    assert redirect_issues[0]['url'] == site.base


def test_pipeline_counts_and_persists_redirect_targets(tmp_path):
    home_html = (
        '<!doctype html><html><head><title>Home</title>'
        '<link rel="canonical" href="/r"></head>'
        '<body><h1>Home</h1><a href="/r">redirect</a></body></html>'
    )
    site = _Site({
        '/': (200, {'Content-Type': 'text/html; charset=utf-8'}, home_html),
        '/r': _redirect('/target/'),
        '/target/': _page('Target'),
    })
    db = Database(str(tmp_path / 'redirects.db'))
    try:
        result = asyncio.run(
            run_scan_pipeline(db, site.base, max_pages=10, ignore_robots=True))
        stored = db.get_scan_results(result['scan_id'])
    finally:
        site.close()
        db.close()

    assert result['html_page_count'] == 2
    assert stored['scan']['total_pages'] == 2
    assert {page['url'] for page in stored['pages']} == {
        site.base, f'{site.base}/target'}
    assert 'canonical_to_redirect' in {
        issue['issue_type'] for issue in result['issues']}


def test_broken_link_through_a_redirect_uses_the_final_status(temp_db):
    site = _Site({
        '/': _page('Home', [('/gone', 'gone')]),
        '/gone': _redirect('/missing'),
        '/missing': (404, {'Content-Type': 'text/html; charset=utf-8'},
                     _html('Missing')),
    })
    try:
        results = asyncio.run(_crawl(site.base))
    finally:
        site.close()

    scan_id = temp_db.create_scan(site.base)
    issues = BrokenLinksModule(temp_db).analyze(scan_id, results)

    broken = [i for i in issues if i['issue_type'] == 'broken_link']
    assert len(broken) == 1
    assert broken[0]['url'] == f'{site.base}/gone'
    assert 'HTTP 404' in broken[0]['description']
