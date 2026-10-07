# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
Unit tests for meta_robots module.
"""
import pytest
from modules.meta_robots import MetaRobotsModule


class TestMetaRobotsModule:
    """Tests for MetaRobotsModule class."""
    
    def test_analyze_noindex(self, temp_db, sample_scan_id):
        """Test detecting noindex directive."""
        module = MetaRobotsModule(temp_db)
        
        html = '''
        <html>
            <head>
                <meta name="robots" content="noindex">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'meta_robots_noindex'
        assert issues[0]['severity'] == 'high'
    
    def test_analyze_nofollow(self, temp_db, sample_scan_id):
        """Test detecting nofollow directive."""
        module = MetaRobotsModule(temp_db)
        
        html = '''
        <html>
            <head>
                <meta name="robots" content="nofollow">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'meta_robots_nofollow'
        assert issues[0]['severity'] == 'medium'
    
    def test_analyze_nosnippet(self, temp_db, sample_scan_id):
        """Test detecting nosnippet directive."""
        module = MetaRobotsModule(temp_db)
        
        html = '''
        <html>
            <head>
                <meta name="robots" content="nosnippet">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'meta_robots_nosnippet'
        assert issues[0]['severity'] == 'medium'
    
    def test_analyze_noarchive(self, temp_db, sample_scan_id):
        """Test detecting noarchive directive."""
        module = MetaRobotsModule(temp_db)
        
        html = '''
        <html>
            <head>
                <meta name="robots" content="noarchive">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'meta_robots_noarchive'
        assert issues[0]['severity'] == 'info'
    
    def test_analyze_multiple_directives(self, temp_db, sample_scan_id):
        """Test detecting multiple directives in one tag."""
        module = MetaRobotsModule(temp_db)
        
        html = '''
        <html>
            <head>
                <meta name="robots" content="noindex, nofollow, nosnippet">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 3
        issue_types = [issue['issue_type'] for issue in issues]
        assert 'meta_robots_noindex' in issue_types
        assert 'meta_robots_nofollow' in issue_types
        assert 'meta_robots_nosnippet' in issue_types
    
    def test_analyze_no_meta_robots(self, temp_db, sample_scan_id):
        """Test that pages without meta robots don't generate issues."""
        module = MetaRobotsModule(temp_db)
        
        html = '''
        <html>
            <head>
                <title>Page</title>
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 0
    
    def test_analyze_case_insensitive(self, temp_db, sample_scan_id):
        """Test that meta name is case-insensitive."""
        module = MetaRobotsModule(temp_db)
        
        html = '''
        <html>
            <head>
                <meta name="ROBOTS" content="noindex">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'meta_robots_noindex'
    
    def test_analyze_content_case_insensitive(self, temp_db, sample_scan_id):
        """Test that content is case-insensitive."""
        module = MetaRobotsModule(temp_db)
        
        html = '''
        <html>
            <head>
                <meta name="robots" content="NOINDEX">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'meta_robots_noindex'
    
    def test_analyze_noimageindex(self, temp_db, sample_scan_id):
        """Test detecting noimageindex directive."""
        module = MetaRobotsModule(temp_db)
        
        html = '''
        <html>
            <head>
                <meta name="robots" content="noimageindex">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'meta_robots_noimageindex'
        assert issues[0]['severity'] == 'medium'
    
    def test_analyze_notranslate(self, temp_db, sample_scan_id):
        """Test detecting notranslate directive."""
        module = MetaRobotsModule(temp_db)
        
        html = '''
        <html>
            <head>
                <meta name="robots" content="notranslate">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'meta_robots_notranslate'
        assert issues[0]['severity'] == 'info'
    
    def test_analyze_unavailable_after(self, temp_db, sample_scan_id):
        """Test detecting unavailable_after directive."""
        module = MetaRobotsModule(temp_db)
        
        html = '''
        <html>
            <head>
                <meta name="robots" content="unavailable_after: 25-Aug-2026 12:00:00 EST">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'meta_robots_unavailable_after'
        assert issues[0]['severity'] == 'info'
    
    def test_analyze_empty_content(self, temp_db, sample_scan_id):
        """Test that empty content is ignored."""
        module = MetaRobotsModule(temp_db)
        
        html = '''
        <html>
            <head>
                <meta name="robots" content="">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 0
    
    def test_analyze_multiple_meta_robots_tags(self, temp_db, sample_scan_id):
        """Test handling multiple meta robots tags."""
        module = MetaRobotsModule(temp_db)
        
        html = '''
        <html>
            <head>
                <meta name="robots" content="noindex">
                <meta name="robots" content="nofollow">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 2
    
    def test_analyze_page_without_html(self, temp_db, sample_scan_id):
        """Test analyzing pages without HTML content."""
        module = MetaRobotsModule(temp_db)
        
        pages = [
            {'url': 'https://example.com', 'html': None},
            {'url': 'https://example.com/page2'}
        ]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 0
    
    def test_analyze_index_follow(self, temp_db, sample_scan_id):
        """Test that index, follow directives don't generate issues."""
        module = MetaRobotsModule(temp_db)
        
        html = '''
        <html>
            <head>
                <meta name="robots" content="index, follow">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 0