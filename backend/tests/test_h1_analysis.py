"""
Unit tests for h1_analysis module.
"""
import pytest
from modules import h1_analysis
from bs4 import BeautifulSoup


class TestH1Analysis:
    """Tests for h1_analysis module."""
    
    def test_analyze_h1_missing(self):
        """Test detecting missing H1 header."""
        html = '<html><body><h2>Content</h2></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = h1_analysis.analyze_h1_headers(soup, 'https://example.com', {})
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'missing_h1'
        assert issues[0]['severity'] == 'high'
    
    def test_analyze_h1_single(self):
        """Test detecting single H1 header (no issues)."""
        html = '<html><body><h1>Main Title</h1></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = h1_analysis.analyze_h1_headers(soup, 'https://example.com', {})
        
        assert len(issues) == 0
    
    def test_analyze_h1_multiple_same_page(self):
        """Test detecting multiple H1 headers on same page."""
        html = '<html><body><h1>Title 1</h1><h1>Title 2</h1></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = h1_analysis.analyze_h1_headers(soup, 'https://example.com', {})
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'multiple_h1_same_page'
        assert issues[0]['severity'] == 'high'
        assert '2 H1 headers' in issues[0]['description']
    
    def test_analyze_h1_duplicate_across_pages(self):
        """Test detecting duplicate H1 across different pages."""
        html1 = '<html><body><h1>Same Title</h1></body></html>'
        html2 = '<html><body><h1>Same Title</h1></body></html>'
        
        soup1 = BeautifulSoup(html1, 'html.parser')
        all_pages_data = {
            'https://example.com/page2': {'html': html2}
        }
        
        issues = h1_analysis.analyze_h1_headers(soup1, 'https://example.com/page1', all_pages_data)
        
        # Should find duplicate on both pages
        assert len(issues) >= 1
        duplicate_issues = [i for i in issues if i['issue_type'] == 'duplicate_h1']
        assert len(duplicate_issues) >= 1
    
    def test_analyze_h1_no_duplicate_different_titles(self):
        """Test that different H1 titles are not flagged as duplicates."""
        html1 = '<html><body><h1>Title 1</h1></body></html>'
        html2 = '<html><body><h1>Title 2</h1></body></html>'
        
        soup1 = BeautifulSoup(html1, 'html.parser')
        all_pages_data = {
            'https://example.com/page2': {'html': html2}
        }
        
        issues = h1_analysis.analyze_h1_headers(soup1, 'https://example.com/page1', all_pages_data)
        
        # Should not find any issues
        assert len(issues) == 0
    
    def test_analyze_h1_case_sensitive_duplicates(self):
        """Test that H1 duplicate detection is case-sensitive."""
        html1 = '<html><body><h1>Same Title</h1></body></html>'
        html2 = '<html><body><h1>same title</h1></body></html>'
        
        soup1 = BeautifulSoup(html1, 'html.parser')
        all_pages_data = {
            'https://example.com/page2': {'html': html2}
        }
        
        issues = h1_analysis.analyze_h1_headers(soup1, 'https://example.com/page1', all_pages_data)
        
        # Should not detect as duplicate due to case sensitivity
        duplicate_issues = [i for i in issues if i['issue_type'] == 'duplicate_h1']
        assert len(duplicate_issues) == 0
    
    def test_analyze_h1_whitespace_ignored(self):
        """Test that whitespace is trimmed from H1 text."""
        html1 = '<html><body><h1>  Same Title  </h1></body></html>'
        html2 = '<html><body><h1>Same Title</h1></body></html>'
        
        soup1 = BeautifulSoup(html1, 'html.parser')
        all_pages_data = {
            'https://example.com/page2': {'html': html2}
        }
        
        issues = h1_analysis.analyze_h1_headers(soup1, 'https://example.com/page1', all_pages_data)
        
        # Should detect as duplicate after trimming whitespace
        duplicate_issues = [i for i in issues if i['issue_type'] == 'duplicate_h1']
        assert len(duplicate_issues) >= 1
    
    def test_analyze_h1_empty_text(self):
        """Test handling H1 with empty text."""
        html = '<html><body><h1></h1></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = h1_analysis.analyze_h1_headers(soup, 'https://example.com', {})
        
        # Empty H1 should be treated as missing
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'missing_h1'
    
    def test_analyze_h1_multiple_empty(self):
        """Test handling multiple H1s with empty text."""
        html = '<html><body><h1></h1><h1></h1></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = h1_analysis.analyze_h1_headers(soup, 'https://example.com', {})
        
        # Multiple empty H1s should be treated as multiple H1s
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'multiple_h1_same_page'
    
    def test_analyze_h1_with_nested_elements(self):
        """Test H1 with nested elements."""
        html = '<html><body><h1><span>Title</span> <strong>Text</strong></h1></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        
        issues = h1_analysis.analyze_h1_headers(soup, 'https://example.com', {})
        
        # Should extract text correctly and not flag as issue
        assert len(issues) == 0
    
    def test_analyze_h1_duplicate_with_nested_elements(self):
        """Test duplicate detection with nested elements."""
        html1 = '<html><body><h1><span>Title</span> Text</h1></body></html>'
        html2 = '<html><body><h1>Title Text</h1></body></html>'
        
        soup1 = BeautifulSoup(html1, 'html.parser')
        all_pages_data = {
            'https://example.com/page2': {'html': html2}
        }
        
        issues = h1_analysis.analyze_h1_headers(soup1, 'https://example.com/page1', all_pages_data)
        
        # Should detect as duplicate (text extraction handles nested elements)
        duplicate_issues = [i for i in issues if i['issue_type'] == 'duplicate_h1']
        assert len(duplicate_issues) >= 1
    
    def test_analyze_h1_self_reference_skipped(self):
        """Test that page doesn't compare H1 with itself."""
        html = '<html><body><h1>Same Title</h1></body></html>'
        
        soup = BeautifulSoup(html, 'html.parser')
        all_pages_data = {
            'https://example.com/page1': {'html': html}
        }
        
        issues = h1_analysis.analyze_h1_headers(soup, 'https://example.com/page1', all_pages_data)
        
        # Should not flag as duplicate when comparing with itself
        duplicate_issues = [i for i in issues if i['issue_type'] == 'duplicate_h1']
        assert len(duplicate_issues) == 0
    
    def test_analyze_h1_multiple_pages_with_duplicates(self):
        """Test detecting duplicates across multiple pages."""
        html = '<html><body><h1>Same Title</h1></body></html>'
        
        soup = BeautifulSoup(html, 'html.parser')
        all_pages_data = {
            'https://example.com/page2': {'html': html},
            'https://example.com/page3': {'html': html},
            'https://example.com/page4': {'html': '<html><body><h1>Different</h1></body></html>'}
        }
        
        issues = h1_analysis.analyze_h1_headers(soup, 'https://example.com/page1', all_pages_data)
        
        # Should find duplicates on page2 and page3
        duplicate_issues = [i for i in issues if i['issue_type'] == 'duplicate_h1']
        assert len(duplicate_issues) >= 1