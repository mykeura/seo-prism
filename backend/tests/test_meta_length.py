# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 mykeura <mykeura@hotmail.com>

"""
Unit tests for meta_length module.
"""
import pytest
from modules.meta_length import MetaLengthModule


class TestMetaLengthModule:
    """Tests for meta_length module."""
    
    def test_title_too_short(self, temp_db, sample_scan_id):
        """Test detecting title that is too short."""
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': '<html><head><title>Short</title></head><body><h1>Test</h1></body></html>',
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'title_too_short'
        assert issues[0]['severity'] == 'medium'
        assert 'too short' in issues[0]['description'].lower()
        assert '5 characters' in issues[0]['description']
    
    def test_title_too_long(self, temp_db, sample_scan_id):
        """Test detecting title that is too long."""
        long_title = 'A' * 100  # 100 characters, exceeds 60 limit
        html = f'<html><head><title>{long_title}</title></head><body><h1>Test</h1></body></html>'
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'title_too_long'
        assert issues[0]['severity'] == 'medium'
        assert 'too long' in issues[0]['description'].lower()
        assert '100 characters' in issues[0]['description']
    
    def test_title_optimal_length(self, temp_db, sample_scan_id):
        """Test that optimal title length (30-60 chars) produces no issues."""
        optimal_title = 'This is an optimal title length for SEO'
        html = f'<html><head><title>{optimal_title}</title></head><body><h1>Test</h1></body></html>'
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_title_exactly_30_chars(self, temp_db, sample_scan_id):
        """Test title with exactly 30 characters (minimum acceptable)."""
        title = 'A' * 30  # Exactly 30 characters
        html = f'<html><head><title>{title}</title></head><body><h1>Test</h1></body></html>'
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_title_exactly_60_chars(self, temp_db, sample_scan_id):
        """Test title with exactly 60 characters (maximum acceptable)."""
        title = 'A' * 60  # Exactly 60 characters
        html = f'<html><head><title>{title}</title></head><body><h1>Test</h1></body></html>'
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_meta_description_too_short(self, temp_db, sample_scan_id):
        """Test detecting meta description that is too short."""
        html = '''<html>
            <head>
                <title>This is an optimal title length for SEO</title>
                <meta name="description" content="Short desc">
            </head>
            <body><h1>Test</h1></body>
        </html>'''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'meta_description_too_short'
        assert issues[0]['severity'] == 'medium'
        assert 'too short' in issues[0]['description'].lower()
    
    def test_meta_description_too_long(self, temp_db, sample_scan_id):
        """Test detecting meta description that is too long."""
        long_desc = 'A' * 200  # 200 characters, exceeds 150 limit
        html = f'''<html>
            <head>
                <title>This is an optimal title length for SEO</title>
                <meta name="description" content="{long_desc}">
            </head>
            <body><h1>Test</h1></body>
        </html>'''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'meta_description_too_long'
        assert issues[0]['severity'] == 'medium'
        assert 'too long' in issues[0]['description'].lower()
        assert '200 characters' in issues[0]['description']
    
    def test_meta_description_optimal_length(self, temp_db, sample_scan_id):
        """Test that optimal meta description length (70-150 chars) produces no issues."""
        optimal_desc = 'This is an optimal meta description length for SEO purposes and ranking'
        html = f'''<html>
            <head>
                <title>This is an optimal title length for SEO</title>
                <meta name="description" content="{optimal_desc}">
            </head>
            <body><h1>Test</h1></body>
        </html>'''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_meta_description_exactly_70_chars(self, temp_db, sample_scan_id):
        """Test meta description with exactly 70 characters (minimum acceptable)."""
        desc = 'A' * 70  # Exactly 70 characters
        html = f'''<html>
            <head>
                <title>This is an optimal title length for SEO</title>
                <meta name="description" content="{desc}">
            </head>
            <body><h1>Test</h1></body>
        </html>'''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_meta_description_exactly_150_chars(self, temp_db, sample_scan_id):
        """Test meta description with exactly 150 characters (maximum acceptable)."""
        desc = 'A' * 150  # Exactly 150 characters
        html = f'''<html>
            <head>
                <title>This is an optimal title length for SEO</title>
                <meta name="description" content="{desc}">
            </head>
            <body><h1>Test</h1></body>
        </html>'''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_both_title_and_meta_issues(self, temp_db, sample_scan_id):
        """Test detecting both title and meta description issues on same page."""
        html = '''<html>
            <head>
                <title>Short</title>
                <meta name="description" content="Short desc">
            </head>
            <body><h1>Test</h1></body>
        </html>'''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 2
        issue_types = [i['issue_type'] for i in issues]
        assert 'title_too_short' in issue_types
        assert 'meta_description_too_short' in issue_types
    
    def test_multiple_pages_with_issues(self, temp_db, sample_scan_id):
        """Test detecting issues across multiple pages."""
        crawled_pages = [
            {
                'url': 'https://example.com/page1',
                'status': 200,
                'html': '<html><head><title>Short</title></head><body><h1>Test</h1></body></html>',
                'links': []
            },
            {
                'url': 'https://example.com/page2',
                'status': 200,
                'html': '<html><head><meta name="description" content="Short"></meta></head><body><h1>Test</h1></body></html>',
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 2
    
    def test_page_without_title(self, temp_db, sample_scan_id):
        """Test page without title tag produces no length issues."""
        html = '<html><head></head><body><h1>Test</h1></body></html>'
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_page_without_meta_description(self, temp_db, sample_scan_id):
        """Test page without meta description produces no length issues."""
        html = '<html><head><title>This is an optimal title length for SEO</title></head><body><h1>Test</h1></body></html>'
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_empty_title(self, temp_db, sample_scan_id):
        """Test page with empty title tag produces no length issues."""
        html = '<html><head><title></title></head><body><h1>Test</h1></body></html>'
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_empty_meta_description(self, temp_db, sample_scan_id):
        """Test page with empty meta description produces no length issues."""
        html = '<html><head><title>This is an optimal title length for SEO</title><meta name="description" content=""></meta></head><body><h1>Test</h1></body></html>'
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_page_without_html(self, temp_db, sample_scan_id):
        """Test page without HTML content produces no issues."""
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': None,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_title_with_whitespace_trimming(self, temp_db, sample_scan_id):
        """Test that whitespace is trimmed from title."""
        html = '<html><head><title>  Short  </title></head><body><h1>Test</h1></body></html>'
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'title_too_short'
        assert '5 characters' in issues[0]['description']  # After trimming
    
    def test_meta_description_with_whitespace_trimming(self, temp_db, sample_scan_id):
        """Test that whitespace is trimmed from meta description."""
        html = '<html><head><title>This is an optimal title length for SEO</title><meta name="description" content="  Short desc  "></meta></head><body><h1>Test</h1></body></html>'
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'meta_description_too_short'
    
    def test_issues_saved_to_database(self, temp_db, sample_scan_id):
        """Test that issues are properly saved to database."""
        html = '<html><head><title>Short</title></head><body><h1>Test</h1></body></html>'
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        # Verify issues were saved to database
        results = temp_db.get_scan_results(sample_scan_id)
        db_issues = results['issues']
        
        assert len(db_issues) == 1
        assert db_issues[0]['issue_type'] == 'title_too_short'
        assert db_issues[0]['url'] == 'https://example.com/page'
        assert db_issues[0]['severity'] == 'medium'
    
    def test_multiple_issues_same_page(self, temp_db, sample_scan_id):
        """Test detecting multiple issues on the same page."""
        long_title = 'A' * 100
        short_desc = 'Short'
        html = f'''<html>
            <head>
                <title>{long_title}</title>
                <meta name="description" content="{short_desc}">
            </head>
            <body><h1>Test</h1></body>
        </html>'''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = MetaLengthModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 2
        issue_types = [i['issue_type'] for i in issues]
        assert 'title_too_long' in issue_types
        assert 'meta_description_too_short' in issue_types