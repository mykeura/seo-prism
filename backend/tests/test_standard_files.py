"""
Integration tests for standard_files module.

Uses a real local HTTP server on an ephemeral port (which also regression-
tests port handling: the historic bug dropped the port and probed port 80,
so local dev servers like `astro dev` on :4321 were never recognized).
"""
import asyncio
import functools
import http.server
import threading

import pytest

from database import Database
from modules.standard_files import StandardFilesModule


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@pytest.fixture
def static_site(tmp_path):
    """Serve tmp_path over HTTP on an ephemeral port."""
    handler = functools.partial(_QuietHandler, directory=str(tmp_path))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_address[1]}', tmp_path
    server.shutdown()
    thread.join()


def _write(root, name, content):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _run_analyze(base_url):
    db = Database(':memory:')
    scan_id = db.create_scan(base_url)
    module = StandardFilesModule(db)
    issues = asyncio.run(module.analyze(scan_id, base_url))
    stored = db.get_scan_results(scan_id)['issues']
    db.close()
    return issues, stored


def _types(issues):
    return {i['issue_type'] for i in issues}


class TestStandardFilesModule:

    def test_astro_scenario(self, static_site):
        """Astro dev layout: sitemap-index.xml + robots.txt + llms.txt in root."""
        base_url, root = static_site
        _write(root, 'robots.txt',
               'User-agent: *\nAllow: /\n\nSitemap: %s/sitemap-index.xml\n' % base_url)
        _write(root, 'sitemap-index.xml',
               '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>')
        _write(root, 'llms.txt', '# Site\n\nDescription for AI models.\n')

        issues, stored = _run_analyze(base_url)
        types = _types(issues)

        assert 'robots_txt_found' in types
        assert 'llms_txt_found' in types
        assert 'sitemap_found' in types
        assert 'missing_sitemap' not in types
        # Regression: everything counted is persisted
        assert len(stored) == len(issues)

    def test_wordpress_core_sitemap(self, static_site):
        """WordPress >= 5.5 default name: wp-sitemap.xml (no robots directive)."""
        base_url, root = static_site
        _write(root, 'wp-sitemap.xml',
               '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>')

        issues, _ = _run_analyze(base_url)
        assert 'sitemap_found' in _types(issues)
        assert 'missing_sitemap' not in _types(issues)

    def test_well_known_sitemap(self, static_site):
        """Well-known URI location: /.well-known/sitemap.xml."""
        base_url, root = static_site
        _write(root, '.well-known/sitemap.xml',
               '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>')

        issues, _ = _run_analyze(base_url)
        assert 'sitemap_found' in _types(issues)
        assert 'missing_sitemap' not in _types(issues)

    def test_custom_sitemap_name_via_robots_directive(self, static_site):
        """A non-standard sitemap name declared in robots.txt is discovered."""
        base_url, root = static_site
        _write(root, 'robots.txt', 'Sitemap: %s/mi-sitemap-personalizado.xml\n' % base_url)
        _write(root, 'mi-sitemap-personalizado.xml',
               '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>')

        issues, _ = _run_analyze(base_url)
        assert 'sitemap_found' in _types(issues)
        found_urls = [i['url'] for i in issues if i['issue_type'] == 'sitemap_found']
        assert any('mi-sitemap-personalizado' in u for u in found_urls)

    def test_all_files_missing(self, static_site):
        base_url, _ = static_site
        issues, _ = _run_analyze(base_url)
        types = _types(issues)

        assert types == {'missing_robots_txt', 'missing_security_txt',
                         'missing_llms_txt', 'missing_sitemap'}

    def test_security_txt_fallback_root_location(self, static_site):
        """security.txt is accepted at /security.txt (legacy root location)."""
        base_url, root = static_site
        _write(root, 'security.txt', 'Contact: mailto:security@example.com\n')

        issues, _ = _run_analyze(base_url)
        assert 'security_txt_found' in _types(issues)

    def test_found_urls_use_the_server_port(self, static_site):
        """The reported URLs must keep the ephemeral port (historic bug: dropped)."""
        base_url, root = static_site
        _write(root, 'robots.txt', 'User-agent: *\nAllow: /\n')

        issues, _ = _run_analyze(base_url)
        found = [i['url'] for i in issues if i['issue_type'] == 'robots_txt_found']
        assert found == [f'{base_url}/robots.txt']
