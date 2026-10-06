# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 mykeura <mykeura@hotmail.com>

"""
Unit tests for duplicate_content module.
"""
import pytest
from modules.duplicate_content import DuplicateContentModule


class TestDuplicateContentModule:
    """Tests for DuplicateContentModule class."""
    
    def test_analyze_duplicate_titles(self, temp_db, sample_scan_id):
        """Test detecting duplicate titles across pages."""
        module = DuplicateContentModule(temp_db)
        
        pages = [
            {
                'url': 'https://example.com/page1',
                'html': '<html><head><title>Same Title</title></head><body>Content 1</body></html>'
            },
            {
                'url': 'https://example.com/page2',
                'html': '<html><head><title>Same Title</title></head><body>Content 2</body></html>'
            },
            {
                'url': 'https://example.com/page3',
                'html': '<html><head><title>Different Title</title></head><body>Content 3</body></html>'
            }
        ]
        
        issues = module.analyze(sample_scan_id, pages)
        
        # Should find duplicate titles on page1 and page2
        duplicate_title_issues = [i for i in issues if i['issue_type'] == 'duplicate_title']
        assert len(duplicate_title_issues) == 2
        assert any('page1' in issue['url'] for issue in duplicate_title_issues)
        assert any('page2' in issue['url'] for issue in duplicate_title_issues)
        assert '2 pages' in duplicate_title_issues[0]['description']
    
    def test_analyze_duplicate_descriptions(self, temp_db, sample_scan_id):
        """Test detecting duplicate meta descriptions across pages."""
        module = DuplicateContentModule(temp_db)
        
        pages = [
            {
                'url': 'https://example.com/page1',
                'html': '<html><head><title>Title 1</title><meta name="description" content="Same Description"></meta></head><body>Content 1</body></html>'
            },
            {
                'url': 'https://example.com/page2',
                'html': '<html><head><title>Title 2</title><meta name="description" content="Same Description"></meta></head><body>Content 2</body></html>'
            }
        ]
        
        issues = module.analyze(sample_scan_id, pages)
        
        duplicate_desc_issues = [i for i in issues if i['issue_type'] == 'duplicate_description']
        assert len(duplicate_desc_issues) == 2
    
    def test_analyze_no_duplicates(self, temp_db, sample_scan_id):
        """Test analyzing pages with no duplicate content."""
        module = DuplicateContentModule(temp_db)
        
        pages = [
            {
                'url': 'https://example.com/page1',
                'html': '<html><head><title>Title 1</title><meta name="description" content="Description 1"></meta></head><body>Content 1</body></html>'
            },
            {
                'url': 'https://example.com/page2',
                'html': '<html><head><title>Title 2</title><meta name="description" content="Description 2"></meta></head><body>Content 2</body></html>'
            }
        ]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 0
    
    def test_analyze_missing_titles(self, temp_db, sample_scan_id):
        """Test that pages without titles don't cause false positives."""
        module = DuplicateContentModule(temp_db)
        
        pages = [
            {
                'url': 'https://example.com/page1',
                'html': '<html><head></head><body>Content 1</body></html>'
            },
            {
                'url': 'https://example.com/page2',
                'html': '<html><head></head><body>Content 2</body></html>'
            }
        ]
        
        issues = module.analyze(sample_scan_id, pages)
        
        # Should not report duplicate titles when both are missing
        duplicate_title_issues = [i for i in issues if i['issue_type'] == 'duplicate_title']
        assert len(duplicate_title_issues) == 0
    
    def test_analyze_missing_descriptions(self, temp_db, sample_scan_id):
        """Test that pages without descriptions don't cause false positives."""
        module = DuplicateContentModule(temp_db)
        
        pages = [
            {
                'url': 'https://example.com/page1',
                'html': '<html><head><title>Title 1</title></head><body>Content 1</body></html>'
            },
            {
                'url': 'https://example.com/page2',
                'html': '<html><head><title>Title 2</title></head><body>Content 2</body></html>'
            }
        ]
        
        issues = module.analyze(sample_scan_id, pages)
        
        # Should not report duplicate descriptions when both are missing
        duplicate_desc_issues = [i for i in issues if i['issue_type'] == 'duplicate_description']
        assert len(duplicate_desc_issues) == 0
    
    def test_analyze_multiple_duplicates(self, temp_db, sample_scan_id):
        """Test detecting multiple duplicate titles."""
        module = DuplicateContentModule(temp_db)
        
        pages = [
            {
                'url': 'https://example.com/page1',
                'html': '<html><head><title>Same Title</title></head><body>Content 1</body></html>'
            },
            {
                'url': 'https://example.com/page2',
                'html': '<html><head><title>Same Title</title></head><body>Content 2</body></html>'
            },
            {
                'url': 'https://example.com/page3',
                'html': '<html><head><title>Same Title</title></head><body>Content 3</body></html>'
            }
        ]
        
        issues = module.analyze(sample_scan_id, pages)
        
        duplicate_title_issues = [i for i in issues if i['issue_type'] == 'duplicate_title']
        assert len(duplicate_title_issues) == 3
        assert '3 pages' in duplicate_title_issues[0]['description']
    
    def test_analyze_case_sensitive_titles(self, temp_db, sample_scan_id):
        """Test that duplicate detection is case-sensitive."""
        module = DuplicateContentModule(temp_db)
        
        pages = [
            {
                'url': 'https://example.com/page1',
                'html': '<html><head><title>Same Title</title></head><body>Content 1</body></html>'
            },
            {
                'url': 'https://example.com/page2',
                'html': '<html><head><title>same title</title></head><body>Content 2</body></html>'
            }
        ]
        
        issues = module.analyze(sample_scan_id, pages)
        
        # Should not detect as duplicate due to case sensitivity
        duplicate_title_issues = [i for i in issues if i['issue_type'] == 'duplicate_title']
        assert len(duplicate_title_issues) == 0
    
    def test_analyze_whitespace_in_titles(self, temp_db, sample_scan_id):
        """Test that whitespace is trimmed from titles."""
        module = DuplicateContentModule(temp_db)
        
        pages = [
            {
                'url': 'https://example.com/page1',
                'html': '<html><head><title>  Same Title  </title></head><body>Content 1</body></html>'
            },
            {
                'url': 'https://example.com/page2',
                'html': '<html><head><title>Same Title</title></head><body>Content 2</body></html>'
            }
        ]
        
        issues = module.analyze(sample_scan_id, pages)
        
        # Should detect as duplicate after trimming whitespace
        duplicate_title_issues = [i for i in issues if i['issue_type'] == 'duplicate_title']
        assert len(duplicate_title_issues) == 2
    
    def test_analyze_pages_without_html(self, temp_db, sample_scan_id):
        """Test analyzing pages without HTML content."""
        module = DuplicateContentModule(temp_db)
        
        pages = [
            {'url': 'https://example.com/page1', 'html': None},
            {'url': 'https://example.com/page2'}
        ]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 0
    
    def test_severity_levels(self, temp_db, sample_scan_id):
        """Test that correct severity levels are assigned."""
        module = DuplicateContentModule(temp_db)
        
        pages = [
            {
                'url': 'https://example.com/page1',
                'html': '<html><head><title>Same Title</title></head><body>Content 1</body></html>'
            },
            {
                'url': 'https://example.com/page2',
                'html': '<html><head><title>Same Title</title></head><body>Content 2</body></html>'
            }
        ]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert all(issue['severity'] == 'medium' for issue in issues)