# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
Regression test: external non-anchor resources must be verified.

Historic bug: crawl() only queued external *anchors* for verification.
Images, scripts and stylesheets hosted on another domain (a CDN, a font
host...) were skipped, so they never reached url_status_map and
BrokenLinksModule reported nothing. The crawl runs against a mocked
aiohttp session, so these tests use no network.
"""
import asyncio

from core.crawler import Crawler
from modules.broken_links import BrokenLinksModule

_BASE = 'http://site.test/'

_PAGE = '''<!doctype html>
<html><head><title>Home</title>
<link rel="stylesheet" href="https://cdn.other.test/broken.css">
<script src="https://cdn.other.test/broken.js"></script>
</head><body>
<img src="https://cdn.other.test/broken.png">
<img src="/local.png">
<a href="https://ext.other.test/page">external</a>
</body></html>'''


class _FakeResponse:
    def __init__(self, status, body=''):
        self.status = status
        self._body = body
        self.headers = {'Content-Type': 'text/html'}

    async def text(self):
        return self._body


class _FakeResponseContext:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self._response

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeSession:
    """Serves the fixture page over GET; every HEAD answers 404."""

    def __init__(self):
        self.head_requests = []

    def get(self, url, **kwargs):
        return _FakeResponseContext(_FakeResponse(200, _PAGE))

    def head(self, url, **kwargs):
        self.head_requests.append(url)
        return _FakeResponseContext(_FakeResponse(404))

    async def close(self):
        pass


def _crawl_results():
    crawler = Crawler(_BASE)
    crawler.session = _FakeSession()
    results = asyncio.run(crawler.crawl(max_pages=10))
    return crawler, results


def _resource_statuses(results):
    return {r['url']: r['status'] for r in results if r.get('is_resource')}


class TestExternalResourceVerification:
    def test_external_non_anchor_resources_are_head_checked(self):
        crawler, results = _crawl_results()
        statuses = _resource_statuses(results)

        # Before the fix these three were never requested and thus absent.
        assert statuses['https://cdn.other.test/broken.css'] == 404
        assert statuses['https://cdn.other.test/broken.js'] == 404
        assert statuses['https://cdn.other.test/broken.png'] == 404

        # Preserved behaviour: same-domain resources and external anchors
        # keep being verified, each exactly once.
        assert statuses['http://site.test/local.png'] == 404
        assert statuses['https://ext.other.test/page'] == 404
        assert len(crawler.session.head_requests) == 5
        assert len(set(crawler.session.head_requests)) == 5

    def test_broken_external_resources_are_reported(self, temp_db):
        _, results = _crawl_results()

        scan_id = temp_db.create_scan(_BASE)
        issues = BrokenLinksModule(temp_db).analyze(scan_id, results)
        issue_types = {i['url']: i['issue_type'] for i in issues}

        assert issue_types['https://cdn.other.test/broken.png'] == 'broken_image'
        assert issue_types['https://cdn.other.test/broken.js'] == 'broken_script'
        assert issue_types['https://cdn.other.test/broken.css'] == 'broken_stylesheet'
