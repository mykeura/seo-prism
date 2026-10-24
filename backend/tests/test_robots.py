# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
Tests for robots.txt compliance (backend/core/robots.py and its
integration in backend/core/crawler.py).

Every end-to-end test runs against a real local HTTP server (the conftest
pattern used by test_error_pages.py), so the robots.txt fetch, the gate and
the Crawl-delay pacing are exercised over actual requests.
"""
import asyncio
import functools
import http.server
import threading
import time

import aiohttp
import pytest
from urllib.robotparser import RobotFileParser

from core.crawler import Crawler, _USER_AGENT
from core.robots import RobotRules, RobotsCache, host_key

_PAGE = '<!doctype html><html><head><title>P</title></head><body><p>body</p></body></html>'


class _RecordingHandler(http.server.SimpleHTTPRequestHandler):
    """Static file server that records every request it receives."""

    def log_message(self, *args):
        pass

    def _record(self):
        self.server.requests.append(
            (self.command, self.path, time.monotonic(),
             self.headers.get('User-Agent', '')))

    def do_HEAD(self):
        self._record()
        super().do_HEAD()

    def do_GET(self):
        self._record()
        if (self.path.split('?')[0] == '/robots.txt'
                and self.server.robots_status is not None):
            self.send_response(self.server.robots_status)
            self.end_headers()
            return
        super().do_GET()


@pytest.fixture
def site(tmp_path):
    """Serve a small site: index linking a public page and a private one.

    Yields (base_url, server); tests write robots.txt into tmp_path and can
    force a robots.txt status via server.robots_status.
    """
    (tmp_path / 'index.html').write_text(
        '<!doctype html><html><head><title>Home</title></head><body>'
        '<a href="/public.html">public</a>'
        '<a href="/private/secret.html">secret</a></body></html>')
    (tmp_path / 'public.html').write_text(_PAGE)
    (tmp_path / 'private').mkdir()
    (tmp_path / 'private' / 'secret.html').write_text(_PAGE)

    handler = functools.partial(_RecordingHandler, directory=str(tmp_path))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    server.requests = []
    server.robots_status = None
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_address[1]}', server
    finally:
        server.shutdown()
        server.server_close()


async def _crawl(base, **kwargs):
    async with Crawler(base, **kwargs) as crawler:
        results = await crawler.crawl(max_pages=10)
    return crawler, results


def _page_urls(results):
    return {r['url'] for r in results if not r.get('is_resource')}


def _requested_paths(server):
    return [path for _, path, _, _ in server.requests]


class TestRobotsGate:
    def test_disallowed_path_is_not_crawled(self, site, tmp_path):
        base, server = site
        (tmp_path / 'robots.txt').write_text('User-agent: *\nDisallow: /private/\n')

        crawler, results = asyncio.run(_crawl(base))

        assert _page_urls(results) == {base, f'{base}/public.html'}
        assert crawler.robots_skipped_count == 1
        assert crawler.robots_skipped_urls == {f'{base}/private/secret.html'}
        # No request of any kind (GET or HEAD) ever hit the disallowed path.
        assert all('/private/' not in path for path in _requested_paths(server))

    def test_robots_txt_is_fetched_with_the_real_user_agent(self, site, tmp_path):
        base, server = site
        (tmp_path / 'robots.txt').write_text('User-agent: *\nDisallow: /private/\n')

        asyncio.run(_crawl(base))

        robots_agents = [agent for _, path, _, agent in server.requests
                         if path == '/robots.txt']
        assert robots_agents == [_USER_AGENT]

    def test_missing_robots_txt_allows_everything(self, site, tmp_path):
        base, server = site
        # No robots.txt file: the server answers 404.

        crawler, results = asyncio.run(_crawl(base))

        assert f'{base}/private/secret.html' in _page_urls(results)
        assert crawler.robots_skipped_count == 0

    def test_unreachable_robots_txt_allows_everything(self, site, tmp_path):
        base, server = site
        server.robots_status = 500

        crawler, results = asyncio.run(_crawl(base))

        assert f'{base}/private/secret.html' in _page_urls(results)
        assert crawler.robots_skipped_count == 0

    def test_disallowed_base_url_crawls_nothing(self, site, tmp_path):
        base, server = site
        (tmp_path / 'robots.txt').write_text('User-agent: *\nDisallow: /\n')

        crawler, results = asyncio.run(_crawl(base))

        assert _page_urls(results) == set()
        assert crawler.robots_skipped_count == 1

    def test_skipped_page_is_not_head_verified_as_resource(self, site, tmp_path):
        base, server = site
        (tmp_path / 'robots.txt').write_text('User-agent: *\nDisallow: /private/\n')

        asyncio.run(_crawl(base))

        private_requests = [path for path in _requested_paths(server)
                            if '/private/' in path]
        assert private_requests == []
        assert '/robots.txt' in _requested_paths(server)


class TestIgnoreRobotsKeepsCurrentBehaviour:
    def test_disallowed_pages_are_crawled_and_robots_is_not_fetched(self, site, tmp_path):
        base, server = site
        (tmp_path / 'robots.txt').write_text('User-agent: *\nDisallow: /private/\n')

        crawler, results = asyncio.run(_crawl(base, ignore_robots=True))

        assert f'{base}/private/secret.html' in _page_urls(results)
        assert crawler.robots_skipped_count == 0
        assert '/robots.txt' not in _requested_paths(server)


class TestProductTokenGroup:
    def test_group_naming_the_bot_is_honored(self, site, tmp_path):
        base, server = site
        (tmp_path / 'robots.txt').write_text(
            'User-agent: SEO-Prism\nDisallow: /private/\n')

        crawler, results = asyncio.run(_crawl(base))

        assert _page_urls(results) == {base, f'{base}/public.html'}
        assert crawler.robots_skipped_urls == {f'{base}/private/secret.html'}

    def test_named_group_beats_star_group(self, site, tmp_path):
        base, server = site
        (tmp_path / 'robots.txt').write_text(
            'User-agent: SEO-Prism\nDisallow:\n\nUser-agent: *\nDisallow: /\n')

        crawler, results = asyncio.run(_crawl(base))

        assert f'{base}/private/secret.html' in _page_urls(results)
        assert crawler.robots_skipped_count == 0


class TestCrawlDelay:
    _INDEX = ('<!doctype html><html><head><title>Home</title></head><body>'
              '<a href="/p1.html">p1</a><a href="/p2.html">p2</a></body></html>')

    def _write_three_pages(self, tmp_path):
        (tmp_path / 'p1.html').write_text(_PAGE)
        (tmp_path / 'p2.html').write_text(_PAGE)
        (tmp_path / 'index.html').write_text(self._INDEX)

    def _page_times(self, server):
        return sorted(t for method, path, t, _ in server.requests
                      if method == 'GET' and path != '/robots.txt')

    def test_crawl_delay_paces_requests_to_the_host(self, site, tmp_path):
        base, server = site
        (tmp_path / 'robots.txt').write_text('User-agent: *\nCrawl-delay: 1\n')
        self._write_three_pages(tmp_path)

        asyncio.run(_crawl(base))

        times = self._page_times(server)
        assert len(times) == 3
        gaps = [b - a for a, b in zip(times, times[1:])]
        assert min(gaps) >= 0.9
        assert times[-1] - times[0] >= 1.8

    def test_no_crawl_delay_keeps_unpaced_behaviour(self, site, tmp_path):
        base, server = site
        self._write_three_pages(tmp_path)

        asyncio.run(_crawl(base))

        times = self._page_times(server)
        assert len(times) == 3
        assert times[-1] - times[0] < 2.0


class TestRulesAreCachedPerHost:
    def test_rules_fetched_once_per_host(self, site, tmp_path):
        base, server = site
        (tmp_path / 'robots.txt').write_text('User-agent: *\nDisallow: /private/\n')

        async def lookups():
            async with aiohttp.ClientSession() as session:
                cache = RobotsCache(session, 'cache-test/1.0')
                first = await cache.rules_for(base)
                second = await cache.rules_for(base)
                assert first is second

        asyncio.run(lookups())

        assert _requested_paths(server).count('/robots.txt') == 1


def _rules(text, base='http://site.test/'):
    parser = RobotFileParser()
    parser.parse(text.splitlines())
    agents = RobotRules._governing_agents(text, _USER_AGENT)
    return RobotRules(parser, _USER_AGENT, host_key(base), agents)


class TestDelayFor:
    def test_crawl_delay(self):
        rules = _rules('User-agent: *\nCrawl-delay: 2\n')
        assert rules.delay_for('http://site.test/page') == 2.0

    def test_request_rate(self):
        rules = _rules('User-agent: *\nRequest-rate: 1/3\n')
        assert rules.delay_for('http://site.test/page') == 3.0

    def test_request_rate_fractional_interval(self):
        rules = _rules('User-agent: *\nRequest-rate: 5/2\n')
        assert rules.delay_for('http://site.test/page') == 0.4

    def test_most_restrictive_wins(self):
        rules = _rules('User-agent: *\nCrawl-delay: 5\nRequest-rate: 1/1\n')
        assert rules.delay_for('http://site.test/page') == 5.0

    def test_no_directives_means_no_pace(self):
        rules = _rules('User-agent: *\nDisallow:\n')
        assert rules.delay_for('http://site.test/page') is None

    def test_other_host_is_not_paced(self):
        rules = _rules('User-agent: *\nCrawl-delay: 2\n')
        assert rules.delay_for('https://other.test/page') is None

    def test_product_token_delay_governs(self):
        rules = _rules(
            'User-agent: *\nCrawl-delay: 1\n\nUser-agent: SEO-Prism\nCrawl-delay: 3\n')
        assert rules.delay_for('http://site.test/page') == 3.0

    def test_allow_all_rules_never_pace(self):
        rules = RobotRules(None, _USER_AGENT, host_key('http://site.test/'))
        assert rules.delay_for('http://site.test/page') is None
        assert rules.can_fetch('http://site.test/page') is True
