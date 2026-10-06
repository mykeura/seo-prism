# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 mykeura <mykeura@hotmail.com>

"""
Unit tests for broken_links module.
"""
import pytest
from modules.broken_links import BrokenLinksModule


class TestBrokenLinksModule:
    """Tests for BrokenLinksModule class."""
    
    def test_should_ignore_url_social_media(self):
        """Test ignoring social media URLs."""
        module = BrokenLinksModule(None)
        
        assert module._should_ignore_url('https://facebook.com/share') is True
        assert module._should_ignore_url('https://twitter.com/intent') is True
        assert module._should_ignore_url('https://instagram.com/p/xyz') is True
        assert module._should_ignore_url('https://linkedin.com/sharing') is True
    
    def test_should_ignore_url_messaging(self):
        """Test ignoring messaging service URLs."""
        module = BrokenLinksModule(None)
        
        assert module._should_ignore_url('mailto:test@example.com') is True
        assert module._should_ignore_url('tel:+1234567890') is True
        assert module._should_ignore_url('https://wa.me/1234567890') is True
        assert module._should_ignore_url('https://t.me/username') is True
        assert module._should_ignore_url('https://discord.gg/invite') is True
    
    def test_should_ignore_url_protocols(self):
        """Test ignoring protocol-based URLs."""
        module = BrokenLinksModule(None)
        
        assert module._should_ignore_url('javascript:void(0)') is True
        assert module._should_ignore_url('data:text/plain,hello') is True
        assert module._should_ignore_url('callto:+1234567890') is True
    
    def test_should_not_ignore_valid_url(self):
        """Test not ignoring valid URLs."""
        module = BrokenLinksModule(None)
        
        assert module._should_ignore_url('https://example.com/page') is False
        assert module._should_ignore_url('http://example.com/resource') is False
        assert module._should_ignore_url('https://subdomain.example.com/path') is False
    
    def test_analyze_with_broken_links(self, temp_db, sample_scan_id):
        """Test analyzing pages with broken links."""
        module = BrokenLinksModule(temp_db)
        
        crawled_pages = [
            {
                'url': 'https://example.com',
                'status': 200,
                'html': '<html><body>Content</body></html>',
                'resources': [
                    {'url': 'https://example.com/page', 'type': 'anchor'},
                    {'url': 'https://example.com/broken', 'type': 'anchor'}
                ]
            },
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': '<html><body>Page</body></html>',
                'resources': []
            },
            {
                'url': 'https://example.com/broken',
                'status': 404,
                'html': None,
                'resources': []
            }
        ]
        
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'broken_link'
        assert issues[0]['url'] == 'https://example.com/broken'
        assert issues[0]['severity'] == 'medium'
    
    def test_analyze_with_no_broken_links(self, temp_db, sample_scan_id):
        """Test analyzing pages with no broken links."""
        module = BrokenLinksModule(temp_db)
        
        crawled_pages = [
            {
                'url': 'https://example.com',
                'status': 200,
                'html': '<html><body>Content</body></html>',
                'resources': [
                    {'url': 'https://example.com/page', 'type': 'anchor'}
                ]
            },
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': '<html><body>Page</body></html>',
                'resources': []
            }
        ]
        
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_analyze_with_ignored_urls(self, temp_db, sample_scan_id):
        """Test that ignored URLs are not reported as broken."""
        module = BrokenLinksModule(temp_db)
        
        crawled_pages = [
            {
                'url': 'https://example.com',
                'status': 200,
                'html': '<html><body>Content</body></html>',
                'resources': [
                    {'url': 'https://example.com/page', 'type': 'anchor'},
                    {'url': 'https://facebook.com/share', 'type': 'anchor'},
                    {'url': 'mailto:test@example.com', 'type': 'anchor'}
                ]
            },
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': '<html><body>Page</body></html>',
                'resources': []
            }
        ]
        
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        # Facebook and mailto links should be ignored, not reported
        assert len(issues) == 0
    
    def test_get_issue_type(self):
        """Test mapping resource types to issue types."""
        module = BrokenLinksModule(None)
        
        assert module._get_issue_type('anchor') == 'broken_link'
        assert module._get_issue_type('image') == 'broken_image'
        assert module._get_issue_type('script') == 'broken_script'
        assert module._get_issue_type('stylesheet') == 'broken_stylesheet'
        assert module._get_issue_type('link') == 'broken_link'
        assert module._get_issue_type('unknown') == 'broken_resource'
    
    def test_get_severity(self):
        """Test determining severity based on status code."""
        module = BrokenLinksModule(None)
        
        assert module._get_severity(500) == 'high'
        assert module._get_severity(503) == 'high'
        assert module._get_severity(404) == 'medium'
        assert module._get_severity(403) == 'medium'
        assert module._get_severity(400) == 'medium'
        assert module._get_severity(200) == 'low'
        assert module._get_severity(301) == 'low'
    
    def test_analyze_with_server_error(self, temp_db, sample_scan_id):
        """Test analyzing pages with server errors (5xx)."""
        module = BrokenLinksModule(temp_db)
        
        crawled_pages = [
            {
                'url': 'https://example.com',
                'status': 200,
                'html': '<html><body>Content</body></html>',
                'resources': [
                    {'url': 'https://example.com/error', 'type': 'anchor'}
                ]
            },
            {
                'url': 'https://example.com/error',
                'status': 500,
                'html': None,
                'resources': []
            }
        ]
        
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['severity'] == 'high'
    
    def test_analyze_prevents_duplicate_reporting(self, temp_db, sample_scan_id):
        """Test that same broken resource is not reported multiple times."""
        module = BrokenLinksModule(temp_db)
        
        crawled_pages = [
            {
                'url': 'https://example.com',
                'status': 200,
                'html': '<html><body>Content</body></html>',
                'resources': [
                    {'url': 'https://example.com/broken', 'type': 'anchor'}
                ]
            },
            {
                'url': 'https://example.com/page2',
                'status': 200,
                'html': '<html><body>Page 2</body></html>',
                'resources': [
                    {'url': 'https://example.com/broken', 'type': 'anchor'}
                ]
            },
            {
                'url': 'https://example.com/broken',
                'status': 404,
                'html': None,
                'resources': []
            }
        ]
        
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        # Should only report the broken link once
        assert len(issues) == 1
        assert issues[0]['url'] == 'https://example.com/broken'

class TestNormalizedResourceLookup:
    """Regression: homepage resources must match normalized page statuses."""

    def test_broken_homepage_link_with_trailing_slash(self, temp_db, sample_scan_id):
        """A '/' link resolves to 'https://example.com/' while the crawler
        stored 'https://example.com' — the status lookup must still match."""
        module = BrokenLinksModule(temp_db)

        crawled_pages = [
            {
                'url': 'https://example.com',  # normalized root, stored by crawler
                'status': 404,
                'html': None,
                'links': [],
                'resources': []
            },
            {
                'url': 'https://example.com/child',
                'status': 200,
                'html': '<html><a href="/">home</a></html>',
                'links': [],
                'resources': [
                    {'url': 'https://example.com/', 'type': 'anchor', 'source': 'https://example.com/child'}
                ]
            }
        ]

        issues = module.analyze(sample_scan_id, crawled_pages)

        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'broken_link'
        assert issues[0]['url'] == 'https://example.com/'

    def test_working_homepage_link_with_trailing_slash(self, temp_db, sample_scan_id):
        """Same shape but status 200 must not produce an issue."""
        module = BrokenLinksModule(temp_db)

        crawled_pages = [
            {
                'url': 'https://example.com',
                'status': 200,
                'html': '<html><a href="/child">c</a></html>',
                'links': [],
                'resources': []
            },
            {
                'url': 'https://example.com/child',
                'status': 200,
                'html': '<html><a href="/">home</a></html>',
                'links': [],
                'resources': [
                    {'url': 'https://example.com/', 'type': 'anchor', 'source': 'https://example.com/child'}
                ]
            }
        ]

        issues = module.analyze(sample_scan_id, crawled_pages)

        assert len(issues) == 0
