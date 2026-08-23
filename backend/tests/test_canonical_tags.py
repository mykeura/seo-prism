"""
Unit tests for canonical_tags module.
"""
import pytest
from modules.canonical_tags import CanonicalTagsModule


class TestCanonicalTagsModule:
    """Tests for CanonicalTagsModule class."""
    
    def test_analyze_missing_canonical(self):
        """Test detecting missing canonical tag."""
        module = CanonicalTagsModule(None)
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': '<html><head><title>Page</title></head><body>Content</body></html>'
            }
        ]
        
        issues = module.analyze(1, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'missing_canonical'
        assert issues[0]['severity'] == 'low'
    
    def test_analyze_self_canonical(self):
        """Test that self-referencing canonical is valid."""
        module = CanonicalTagsModule(None)
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': '<html><head><link rel="canonical" href="https://example.com/page"></head><body>Content</body></html>'
            }
        ]
        
        issues = module.analyze(1, crawled_pages)
        
        assert len(issues) == 0
    
    def test_analyze_canonical_to_404(self):
        """Test detecting canonical pointing to 404 page."""
        module = CanonicalTagsModule(None)
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': '<html><head><link rel="canonical" href="https://example.com/not-found"></head><body>Content</body></html>'
            },
            {
                'url': 'https://example.com/not-found',
                'status': 404,
                'html': None
            }
        ]
        
        issues = module.analyze(1, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'canonical_to_404'
        assert issues[0]['severity'] == 'high'
    
    def test_analyze_canonical_to_redirect(self):
        """Test detecting canonical pointing to redirect."""
        module = CanonicalTagsModule(None)
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': '<html><head><link rel="canonical" href="https://example.com/redirected"></head><body>Content</body></html>'
            },
            {
                'url': 'https://example.com/redirected',
                'status': 301,
                'html': None
            }
        ]
        
        issues = module.analyze(1, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'canonical_to_redirect'
        assert issues[0]['severity'] == 'medium'
    
    def test_analyze_circular_canonical_chain(self):
        """Test detecting circular canonical chain."""
        module = CanonicalTagsModule(None)
        
        crawled_pages = [
            {
                'url': 'https://example.com/page1',
                'status': 200,
                'html': '<html><head><link rel="canonical" href="https://example.com/page2"></head><body>Content</body></html>'
            },
            {
                'url': 'https://example.com/page2',
                'status': 200,
                'html': '<html><head><link rel="canonical" href="https://example.com/page1"></head><body>Content</body></html>'
            }
        ]
        
        issues = module.analyze(1, crawled_pages)
        
        assert len(issues) >= 1
        circular_issues = [i for i in issues if i['issue_type'] == 'canonical_chain']
        assert len(circular_issues) >= 1
    
    def test_analyze_relative_canonical(self):
        """Test resolving relative canonical URLs."""
        module = CanonicalTagsModule(None)
        
        crawled_pages = [
            {
                'url': 'https://example.com/dir/page',
                'status': 200,
                'html': '<html><head><link rel="canonical" href="/canonical-page"></head><body>Content</body></html>'
            },
            {
                'url': 'https://example.com/canonical-page',
                'status': 200,
                'html': '<html><head><link rel="canonical" href="https://example.com/canonical-page"></head><body>Content</body></html>'
            }
        ]
        
        issues = module.analyze(1, crawled_pages)
        
        # Should resolve relative URL and not flag as issue
        chain_issues = [i for i in issues if i['issue_type'] == 'canonical_chain']
        assert len(chain_issues) == 0
    
    def test_analyze_empty_canonical_href(self):
        """Test detecting empty canonical href."""
        module = CanonicalTagsModule(None)
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': '<html><head><link rel="canonical" href=""></head><body>Content</body></html>'
            }
        ]
        
        issues = module.analyze(1, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'empty_canonical'
    
    def test_analyze_development_environment(self):
        """Test that URL variations are ignored in development."""
        module = CanonicalTagsModule(None)
        
        crawled_pages = [
            {
                'url': 'http://localhost:3000/page',
                'status': 200,
                'html': '<html><head><link rel="canonical" href="https://localhost:3000/page"></head><body>Content</body></html>'
            }
        ]
        
        issues = module.analyze(1, crawled_pages)
        
        # Should not flag http/https variation in development
        variation_issues = [i for i in issues if i['issue_type'] == 'canonical_url_variation']
        assert len(variation_issues) == 0
    
    def test_analyze_multiple_pages_with_canonicals(self):
        """Test analyzing multiple pages with canonicals."""
        module = CanonicalTagsModule(None)
        
        crawled_pages = [
            {
                'url': 'https://example.com/page1',
                'status': 200,
                'html': '<html><head><link rel="canonical" href="https://example.com/page1"></head><body>Content</body></html>'
            },
            {
                'url': 'https://example.com/page2',
                'status': 200,
                'html': '<html><head><link rel="canonical" href="https://example.com/page2"></head><body>Content</body></html>'
            },
            {
                'url': 'https://example.com/page3',
                'status': 200,
                'html': '<html><head><link rel="canonical" href="https://example.com/not-found"></head><body>Content</body></html>'
            },
            {
                'url': 'https://example.com/not-found',
                'status': 404,
                'html': None
            }
        ]
        
        issues = module.analyze(1, crawled_pages)
        
        # Should only find the 404 issue
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'canonical_to_404'
    
    def test_normalize_url(self):
        """Test URL normalization."""
        module = CanonicalTagsModule(None)
        
        url1 = module._normalize_url('https://example.com/page/')
        url2 = module._normalize_url('https://example.com/page')
        
        assert url1 == url2
    
    def test_normalize_url_with_fragment(self):
        """Test that fragments are removed during normalization."""
        module = CanonicalTagsModule(None)
        
        url1 = module._normalize_url('https://example.com/page#section')
        url2 = module._normalize_url('https://example.com/page')
        
        assert url1 == url2
    
    def test_has_url_variation(self):
        """Test detecting URL variations."""
        module = CanonicalTagsModule(None)
        
        assert module._has_url_variation('https://example.com/page', 'https://www.example.com/page') is True
        assert module._has_url_variation('http://example.com/page', 'https://example.com/page') is True
        assert module._has_url_variation('https://example.com/page', 'https://example.com/other') is False
    
    def test_is_development_environment(self):
        """Test detecting development environments."""
        module = CanonicalTagsModule(None)
        
        assert module._is_development_environment('http://localhost:3000') is True
        assert module._is_development_environment('http://127.0.0.1:8080') is True
        assert module._is_development_environment('http://192.168.1.1') is True
        assert module._is_development_environment('https://example.com') is False
    
    def test_extract_canonical(self):
        """Test extracting canonical URL from HTML."""
        module = CanonicalTagsModule(None)
        
        html = '<html><head><link rel="canonical" href="https://example.com/page"></head><body>Content</body></html>'
        canonical = module._extract_canonical(html, 'https://example.com/base')
        
        assert canonical == 'https://example.com/page'
    
    def test_extract_canonical_relative(self):
        """Test extracting relative canonical URL."""
        module = CanonicalTagsModule(None)
        
        html = '<html><head><link rel="canonical" href="/page"></head><body>Content</body></html>'
        canonical = module._extract_canonical(html, 'https://example.com/dir/base')
        
        assert canonical == 'https://example.com/page'

class TestCanonicalTagsPersistence:
    """Regression: canonical issues must be persisted, not just counted.

    Historic bug: the module returned issues but never called db.add_issue,
    so canonical findings were invisible in the web UI, CLI, JSON and
    reports while still inflating total_issues and the SEO grade.
    """

    def test_issues_are_persisted_to_database(self, tmp_path):
        from database import Database

        db = Database(str(tmp_path / 'test_scans.db'))
        scan_id = db.create_scan('https://example.com')

        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': '<html><head><title>Page</title></head><body>Content</body></html>'
            },
            {
                'url': 'https://example.com/other',
                'status': 200,
                'html': '<html><head><link rel="canonical" href=""></head><body>Other</body></html>'
            },
        ]

        module = CanonicalTagsModule(db)
        returned = module.analyze(scan_id, crawled_pages)
        stored = db.get_scan_results(scan_id)['issues']

        assert len(returned) == 2
        assert len(stored) == 2, 'los issues canónicos deben persistirse en la BD'
        assert {i['issue_type'] for i in stored} == {'missing_canonical', 'empty_canonical'}
        db.close()

    def test_db_none_still_returns_issues(self):
        """Unit-test compatibility: analyze works without a database."""
        module = CanonicalTagsModule(None)
        pages = [{
            'url': 'https://example.com/page', 'status': 200,
            'html': '<html><head></head><body></body></html>'
        }]
        assert len(module.analyze(1, pages)) == 1
