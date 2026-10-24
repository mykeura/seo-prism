# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
Unit tests for spa_detection module.
"""
from modules.description_translations import translate_description
from modules.spa_detection import SpaDetectionModule


def page(url, html, **extra):
    data = {'url': url, 'status': 200, 'html': html, 'links': [], 'resources': []}
    data.update(extra)
    return data


NORMAL_HTML = (
    '<!DOCTYPE html><html><head><title>Example Domain</title>'
    '<meta name="description" content="An example page"></head>'
    '<body><div id="main"><h1>Example Domain</h1>'
    '<p>This domain is for use in illustrative examples.</p></div>'
    '<script src="/static/main.js"></script></body></html>'
)

REACT_SHELL_HTML = (
    '<!DOCTYPE html><html><head><title>My App</title></head><body>'
    '<div id="root"></div>'
    '<noscript>You need to enable JavaScript to run this app.</noscript>'
    '<script src="/static/js/main.abc123.js"></script>'
    '<script src="/static/js/react.production.min.js"></script>'
    '</body></html>'
)


class TestSpaSignals:
    """Tests for the per-page JS-rendered heuristics."""

    def setup_method(self):
        self.module = SpaDetectionModule(None)

    def test_react_shell_is_detected(self):
        assert self.module._looks_js_rendered(REACT_SHELL_HTML) is True

    def test_empty_root_container_is_detected(self):
        html = '<html><body><div id="root"></div><script src="/static/app.js"></script></body></html>'
        assert self.module._looks_js_rendered(html) is True

    def test_root_container_with_only_scripts_is_detected(self):
        html = ('<html><body><div id="app"><script>console.log("boot")</script>'
                '<template><p>Hi</p></template></div></body></html>')
        assert self.module._looks_js_rendered(html) is True

    def test_filled_root_container_is_not_detected(self):
        html = ('<html><body><div id="root"><h1>Welcome</h1>'
                '<p>Serve-rendered content.</p></div></body></html>')
        assert self.module._looks_js_rendered(html) is False

    def test_noscript_javascript_warning_is_detected(self):
        html = ('<html><body><h1>Content</h1>'
                '<noscript>Please enable JavaScript to view this site.</noscript>'
                '</body></html>')
        assert self.module._looks_js_rendered(html) is True

    def test_noscript_without_javascript_warning_is_not_detected(self):
        html = ('<html><body><h1>Content</h1>'
                '<noscript><img src="/pixel.gif" alt=""></noscript>'
                '</body></html>')
        assert self.module._looks_js_rendered(html) is False

    def test_framework_marker_is_detected(self):
        assert self.module._looks_js_rendered(
            '<html><body data-v-app=""><h1>Content</h1></body></html>') is True
        assert self.module._looks_js_rendered(
            '<html><head><script>window.__NEXT_DATA__ = {}</script></head>'
            '<body><h1>Content</h1></body></html>') is True

    def test_framework_script_src_is_detected(self):
        html = ('<html><body><h1>Content</h1>'
                '<script src="/vendor/vue.global.prod.js"></script></body></html>')
        assert self.module._looks_js_rendered(html) is True

    def test_normal_html_is_not_detected(self):
        assert self.module._looks_js_rendered(NORMAL_HTML) is False

    def test_wordpress_like_html_is_not_detected(self):
        html = ('<html><head><title>Blog</title></head><body>'
                '<div id="main"><h1>Blog</h1><p>Plenty of server-rendered text.</p></div>'
                '<script src="/wp-content/themes/theme/main.js"></script>'
                '</body></html>')
        assert self.module._looks_js_rendered(html) is False


class TestSpaDetectionModule:
    """Tests for the site-level analyze() output."""

    def test_all_pages_js_rendered_emits_one_issue(self, temp_db, sample_scan_id):
        module = SpaDetectionModule(temp_db)

        issues = module.analyze(sample_scan_id, [
            page('https://example.com/', REACT_SHELL_HTML),
            page('https://example.com/about', REACT_SHELL_HTML.replace('id="root"', 'id="app"')),
        ], 'https://example.com')

        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'spa_detected'
        assert issues[0]['severity'] == 'low'
        assert issues[0]['url'] == 'https://example.com'
        assert issues[0]['description'] == SpaDetectionModule.DESCRIPTION

        cursor = temp_db.conn.cursor()
        cursor.execute('SELECT issue_type, severity FROM issues WHERE scan_id = ?', (sample_scan_id,))
        assert [tuple(row) for row in cursor.fetchall()] == [('spa_detected', 'low')]

    def test_below_threshold_emits_no_issue(self, temp_db, sample_scan_id):
        module = SpaDetectionModule(temp_db)

        issues = module.analyze(sample_scan_id, [
            page('https://example.com/', REACT_SHELL_HTML),
            page('https://example.com/a', NORMAL_HTML),
            page('https://example.com/b', NORMAL_HTML),
        ], 'https://example.com')

        assert issues == []
        cursor = temp_db.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM issues WHERE scan_id = ?', (sample_scan_id,))
        assert cursor.fetchone()[0] == 0

    def test_threshold_is_inclusive(self, temp_db, sample_scan_id):
        module = SpaDetectionModule(temp_db)

        issues = module.analyze(sample_scan_id, [
            page('https://example.com/', REACT_SHELL_HTML),
            page('https://example.com/about', NORMAL_HTML),
        ], 'https://example.com')

        assert len(issues) == 1

    def test_pages_without_html_do_not_count(self, temp_db, sample_scan_id):
        module = SpaDetectionModule(temp_db)

        issues = module.analyze(sample_scan_id, [
            page('https://example.com/', REACT_SHELL_HTML),
            page('https://example.com/404', None, status=404),
            page('https://example.com/broken', None, status=0),
        ], 'https://example.com')

        assert len(issues) == 1

    def test_resource_pages_do_not_count(self, temp_db, sample_scan_id):
        module = SpaDetectionModule(temp_db)

        issues = module.analyze(sample_scan_id, [
            page('https://example.com/app.js', REACT_SHELL_HTML, is_resource=True),
            page('https://example.com/', NORMAL_HTML),
        ], 'https://example.com')

        assert issues == []

    def test_empty_crawl_emits_no_issue(self, temp_db, sample_scan_id):
        module = SpaDetectionModule(temp_db)
        assert module.analyze(sample_scan_id, [], 'https://example.com') == []

    def test_description_is_translated_to_spanish(self):
        translated = translate_description('es', SpaDetectionModule.DESCRIPTION)

        assert translated != SpaDetectionModule.DESCRIPTION
        assert 'SPA' in translated
        assert 'HTML sin renderizar' in translated
        assert translate_description('en', SpaDetectionModule.DESCRIPTION) \
            == SpaDetectionModule.DESCRIPTION
