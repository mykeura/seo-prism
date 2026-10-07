# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
Unit tests for image_alt_text module.
"""
import pytest
from modules.image_alt_text import ImageAltTextModule


class TestImageAltTextModule:
    """Tests for ImageAltTextModule class."""
    
    def test_analyze_missing_alt_text(self, temp_db, sample_scan_id):
        """Test detecting images without alt attribute."""
        module = ImageAltTextModule(temp_db)
        
        html = '''
        <html>
            <body>
                <img src="image1.jpg" />
                <img src="image2.jpg" />
            </body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 2
        assert issues[0]['issue_type'] == 'missing_alt_text'
        assert issues[1]['issue_type'] == 'missing_alt_text'
    
    def test_analyze_empty_alt_text(self, temp_db, sample_scan_id):
        """Test detecting images with empty alt attribute."""
        module = ImageAltTextModule(temp_db)
        
        html = '''
        <html>
            <body>
                <img src="image1.jpg" alt="" />
                <img src="image2.jpg" alt="  " />
            </body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 2
        assert all(issue['issue_type'] == 'missing_alt_text' for issue in issues)
    
    def test_analyze_short_alt_text(self, temp_db, sample_scan_id):
        """Test detecting images with very short alt text."""
        module = ImageAltTextModule(temp_db)
        
        html = '''
        <html>
            <body>
                <img src="image1.jpg" alt="abc" />
                <img src="image2.jpg" alt="12" />
                <img src="image3.jpg" alt="x" />
            </body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 3
        assert all(issue['issue_type'] == 'short_alt_text' for issue in issues)
    
    def test_analyze_valid_alt_text(self, temp_db, sample_scan_id):
        """Test that images with valid alt text are not reported."""
        module = ImageAltTextModule(temp_db)
        
        html = '''
        <html>
            <body>
                <img src="image1.jpg" alt="A beautiful sunset over the ocean" />
                <img src="image2.jpg" alt="Product screenshot showing the dashboard" />
            </body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 0
    
    def test_analyze_mixed_alt_text(self, temp_db, sample_scan_id):
        """Test analyzing pages with mixed alt text quality."""
        module = ImageAltTextModule(temp_db)
        
        html = '''
        <html>
            <body>
                <img src="valid.jpg" alt="This is a good description" />
                <img src="missing.jpg" />
                <img src="empty.jpg" alt="" />
                <img src="short.jpg" alt="bad" />
            </body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 3
        issue_types = [issue['issue_type'] for issue in issues]
        assert 'missing_alt_text' in issue_types
        assert 'short_alt_text' in issue_types
    
    def test_analyze_multiple_pages(self, temp_db, sample_scan_id):
        """Test analyzing multiple pages."""
        module = ImageAltTextModule(temp_db)
        
        pages = [
            {
                'url': 'https://example.com/page1',
                'html': '<html><body><img src="img1.jpg" /></body></html>'
            },
            {
                'url': 'https://example.com/page2',
                'html': '<html><body><img src="img2.jpg" alt="Valid" /></body></html>'
            },
            {
                'url': 'https://example.com/page3',
                'html': '<html><body><img src="img3.jpg" alt="" /></body></html>'
            }
        ]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 2
        assert any('page1' in issue['url'] for issue in issues)
        assert any('page3' in issue['url'] for issue in issues)
    
    def test_analyze_page_without_html(self, temp_db, sample_scan_id):
        """Test analyzing pages without HTML content."""
        module = ImageAltTextModule(temp_db)
        
        pages = [
            {'url': 'https://example.com', 'html': None},
            {'url': 'https://example.com/page2'}
        ]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 0
    
    def test_analyze_page_without_images(self, temp_db, sample_scan_id):
        """Test analyzing pages without images."""
        module = ImageAltTextModule(temp_db)
        
        html = '<html><body><p>No images here</p></body></html>'
        pages = [{'url': 'https://example.com', 'html': html}]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 0
    
    def test_severity_levels(self, temp_db, sample_scan_id):
        """Test that correct severity levels are assigned."""
        module = ImageAltTextModule(temp_db)
        
        html = '''
        <html>
            <body>
                <img src="image1.jpg" />
                <img src="image2.jpg" alt="abc" />
            </body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        missing_issues = [i for i in issues if i['issue_type'] == 'missing_alt_text']
        short_issues = [i for i in issues if i['issue_type'] == 'short_alt_text']
        
        assert all(issue['severity'] == 'medium' for issue in missing_issues)
        assert all(issue['severity'] == 'low' for issue in short_issues)