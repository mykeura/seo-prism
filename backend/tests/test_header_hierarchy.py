# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 mykeura <mykeura@hotmail.com>

"""
Unit tests for header_hierarchy module.
"""
import pytest
from modules import header_hierarchy
from bs4 import BeautifulSoup


class TestHeaderHierarchy:
    """Tests for header_hierarchy module."""
    
    def test_analyze_valid_hierarchy(self):
        """Test analyzing valid header hierarchy."""
        html = '''
        <html>
            <body>
                <h1>Main Title</h1>
                <h2>Section 1</h2>
                <h3>Subsection 1.1</h3>
                <h2>Section 2</h2>
                <h3>Subsection 2.1</h3>
                <h4>Sub-subsection 2.1.1</h4>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = header_hierarchy.analyze_header_hierarchy(soup, 'https://example.com')
        
        assert len(issues) == 0
    
    def test_analyze_no_headers(self):
        """Test analyzing page with no headers."""
        html = '<html><body><p>No headers here</p></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = header_hierarchy.analyze_header_hierarchy(soup, 'https://example.com')
        
        assert len(issues) == 0
    
    def test_analyze_invalid_hierarchy_skip_level(self):
        """Test detecting invalid hierarchy (skipping level)."""
        html = '''
        <html>
            <body>
                <h1>Main Title</h1>
                <h3>Skipped H2</h3>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = header_hierarchy.analyze_header_hierarchy(soup, 'https://example.com')
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'invalid_header_hierarchy'
        assert 'H1 -> H3' in issues[0]['description']
        assert issues[0]['severity'] == 'medium'
    
    def test_analyze_invalid_hierarchy_multiple_skips(self):
        """Test detecting multiple invalid hierarchy jumps."""
        html = '''
        <html>
            <body>
                <h1>Main Title</h1>
                <h2>Section 1</h2>
                <h4>Skipped H3</h4>
                <h2>Section 2</h2>
                <h5>Skipped H3 and H4</h5>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = header_hierarchy.analyze_header_hierarchy(soup, 'https://example.com')
        
        assert len(issues) == 2
        assert all(issue['issue_type'] == 'invalid_header_hierarchy' for issue in issues)
    
    def test_analyze_valid_backward_jump(self):
        """Test that backward jumps are valid."""
        html = '''
        <html>
            <body>
                <h1>Main Title</h1>
                <h2>Section 1</h2>
                <h3>Subsection 1.1</h3>
                <h2>Section 2</h2>
                <h2>Section 3</h2>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = header_hierarchy.analyze_header_hierarchy(soup, 'https://example.com')
        
        assert len(issues) == 0
    
    def test_analyze_only_h1(self):
        """Test analyzing page with only H1."""
        html = '<html><body><h1>Main Title</h1></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = header_hierarchy.analyze_header_hierarchy(soup, 'https://example.com')
        
        assert len(issues) == 0
    
    def test_analyze_same_level_consecutive(self):
        """Test that same level consecutive headers are valid."""
        html = '''
        <html>
            <body>
                <h1>Main Title</h1>
                <h2>Section 1</h2>
                <h2>Section 2</h2>
                <h2>Section 3</h2>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = header_hierarchy.analyze_header_hierarchy(soup, 'https://example.com')
        
        assert len(issues) == 0
    
    def test_analyze_complex_valid_hierarchy(self):
        """Test analyzing complex but valid hierarchy."""
        html = '''
        <html>
            <body>
                <h1>Main Title</h1>
                <h2>Section 1</h2>
                <h3>Subsection 1.1</h3>
                <h4>Sub-subsection 1.1.1</h4>
                <h3>Subsection 1.2</h3>
                <h2>Section 2</h2>
                <h3>Subsection 2.1</h3>
                <h4>Sub-subsection 2.1.1</h4>
                <h5>Sub-sub-subsection 2.1.1.1</h5>
                <h6>Deepest level</h6>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = header_hierarchy.analyze_header_hierarchy(soup, 'https://example.com')
        
        assert len(issues) == 0
    
    def test_analyze_invalid_starting_with_h2(self):
        """Test that starting with H2 (no H1) is valid for hierarchy check."""
        html = '''
        <html>
            <body>
                <h2>Section 1</h2>
                <h3>Subsection</h3>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = header_hierarchy.analyze_header_hierarchy(soup, 'https://example.com')
        
        assert len(issues) == 0
    
    def test_analyze_invalid_starting_with_h3(self):
        """Test detecting invalid hierarchy when starting with H3."""
        html = '''
        <html>
            <body>
                <h3>Section 1</h3>
                <h4>Subsection</h4>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = header_hierarchy.analyze_header_hierarchy(soup, 'https://example.com')
        
        # No H1 before H3, so it's valid (no previous level to compare)
        assert len(issues) == 0
    
    def test_analyze_mixed_valid_invalid(self):
        """Test analyzing mixed valid and invalid hierarchy."""
        html = '''
        <html>
            <body>
                <h1>Main Title</h1>
                <h2>Section 1</h2>
                <h4>Invalid: Skip to H4</h4>
                <h2>Section 2</h2>
                <h3>Subsection 2.1</h3>
                <h5>Invalid: Skip to H5</h5>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = header_hierarchy.analyze_header_hierarchy(soup, 'https://example.com')
        
        assert len(issues) == 2
    
    def test_analyze_case_insensitive_header_tags(self):
        """Test that header tags are case-insensitive."""
        html = '''
        <html>
            <body>
                <H1>Main Title</H1>
                <H2>Section 1</H2>
                <H3>Subsection</H3>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = header_hierarchy.analyze_header_hierarchy(soup, 'https://example.com')
        
        assert len(issues) == 0
    
    def test_analyze_description_format(self):
        """Test that issue description is properly formatted."""
        html = '''
        <html>
            <body>
                <h1>Main Title</h1>
                <h3>Skipped H2</h3>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = header_hierarchy.analyze_header_hierarchy(soup, 'https://example.com')
        
        assert len(issues) == 1
        assert 'H1 -> H3' in issues[0]['description']
        assert 'expected H2' in issues[0]['description']