"""
Unit tests for hreflang module.
"""
import pytest
from modules.hreflang import HreflangModule


class TestHreflangModule:
    """Tests for HreflangModule class."""
    
    def test_analyze_missing_self_reference(self, temp_db, sample_scan_id):
        """Test detecting missing self-referencing hreflang."""
        module = HreflangModule(temp_db)
        
        html = '''
        <html>
            <head>
                <link rel="alternate" hreflang="en" href="https://example.com/en">
                <link rel="alternate" hreflang="es" href="https://example.com/es">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) >= 1
        missing_self = [i for i in issues if i['issue_type'] == 'hreflang_missing_self_reference']
        assert len(missing_self) >= 1
    
    def test_analyze_valid_self_reference(self, temp_db, sample_scan_id):
        """Test that valid self-reference is not flagged."""
        module = HreflangModule(temp_db)
        
        html = '''
        <html>
            <head>
                <link rel="alternate" hreflang="en" href="https://example.com/en">
                <link rel="alternate" hreflang="es" href="https://example.com/es">
                <link rel="alternate" hreflang="x-default" href="https://example.com">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        # Should not have missing self-reference issue
        missing_self = [i for i in issues if i['issue_type'] == 'hreflang_missing_self_reference']
        assert len(missing_self) == 0
    
    def test_analyze_missing_x_default(self, temp_db, sample_scan_id):
        """Test detecting missing x-default hreflang."""
        module = HreflangModule(temp_db)
        
        html = '''
        <html>
            <head>
                <link rel="alternate" hreflang="en" href="https://example.com/en">
                <link rel="alternate" hreflang="es" href="https://example.com/es">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) >= 1
        missing_x_default = [i for i in issues if i['issue_type'] == 'hreflang_missing_x_default']
        assert len(missing_x_default) >= 1
    
    def test_analyze_duplicate_codes(self, temp_db, sample_scan_id):
        """Test detecting duplicate hreflang codes."""
        module = HreflangModule(temp_db)
        
        html = '''
        <html>
            <head>
                <link rel="alternate" hreflang="en" href="https://example.com/en">
                <link rel="alternate" hreflang="en" href="https://example.com/en-us">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) >= 1
        duplicate_codes = [i for i in issues if i['issue_type'] == 'hreflang_duplicate_code']
        assert len(duplicate_codes) >= 1
    
    def test_analyze_invalid_codes(self, temp_db, sample_scan_id):
        """Test detecting invalid hreflang codes."""
        module = HreflangModule(temp_db)
        
        html = '''
        <html>
            <head>
                <link rel="alternate" hreflang="en" href="https://example.com/en">
                <link rel="alternate" hreflang="invalid" href="https://example.com/invalid">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) >= 1
        invalid_codes = [i for i in issues if i['issue_type'] == 'hreflang_invalid_code']
        assert len(invalid_codes) >= 1
    
    def test_analyze_valid_codes(self, temp_db, sample_scan_id):
        """Test that valid codes are not flagged."""
        module = HreflangModule(temp_db)
        
        html = '''
        <html>
            <head>
                <link rel="alternate" hreflang="en" href="https://example.com/en">
                <link rel="alternate" hreflang="es" href="https://example.com/es">
                <link rel="alternate" hreflang="fr" href="https://example.com/fr">
                <link rel="alternate" hreflang="x-default" href="https://example.com">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        # Should not have invalid code issues
        invalid_codes = [i for i in issues if i['issue_type'] == 'hreflang_invalid_code']
        assert len(invalid_codes) == 0
    
    def test_analyze_no_hreflang_tags(self, temp_db, sample_scan_id):
        """Test that pages without hreflang don't generate issues."""
        module = HreflangModule(temp_db)
        
        html = '<html><head><title>Page</title></head><body>Content</body></html>'
        pages = [{'url': 'https://example.com', 'html': html}]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 0
    
    def test_analyze_missing_return_link(self, temp_db, sample_scan_id):
        """Test detecting missing return links."""
        module = HreflangModule(temp_db)
        
        html1 = '''
        <html>
            <head>
                <link rel="alternate" hreflang="en" href="https://example.com/en">
                <link rel="alternate" hreflang="es" href="https://example.com/es">
            </head>
            <body>Content</body>
        </html>
        '''
        
        html2 = '''
        <html>
            <head>
                <link rel="alternate" hreflang="es" href="https://example.com/es">
                <!-- Missing return link to en -->
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [
            {'url': 'https://example.com/en', 'html': html1},
            {'url': 'https://example.com/es', 'html': html2}
        ]
        
        issues = module.analyze(sample_scan_id, pages)
        
        # Should find missing return link
        missing_return = [i for i in issues if i['issue_type'] == 'hreflang_missing_return_link']
        assert len(missing_return) >= 1
    
    def test_analyze_missing_canonical(self, temp_db, sample_scan_id):
        """Test detecting missing canonical when hreflang is present."""
        module = HreflangModule(temp_db)
        
        html = '''
        <html>
            <head>
                <link rel="alternate" hreflang="en" href="https://example.com/en">
                <!-- No canonical tag -->
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) >= 1
        missing_canonical = [i for i in issues if i['issue_type'] == 'hreflang_missing_canonical']
        assert len(missing_canonical) >= 1
    
    def test_analyze_valid_with_canonical(self, temp_db, sample_scan_id):
        """Test that hreflang with canonical is valid."""
        module = HreflangModule(temp_db)
        
        html = '''
        <html>
            <head>
                <link rel="canonical" href="https://example.com">
                <link rel="alternate" hreflang="en" href="https://example.com/en">
                <link rel="alternate" hreflang="x-default" href="https://example.com">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        # Should not have missing canonical issue
        missing_canonical = [i for i in issues if i['issue_type'] == 'hreflang_missing_canonical']
        assert len(missing_canonical) == 0
    
    def test_analyze_region_codes(self, temp_db, sample_scan_id):
        """Test that region codes (en-US, es-ES) are valid."""
        module = HreflangModule(temp_db)
        
        html = '''
        <html>
            <head>
                <link rel="alternate" hreflang="en-US" href="https://example.com/en-us">
                <link rel="alternate" hreflang="es-ES" href="https://example.com/es-es">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        # Should not flag region codes as invalid
        invalid_codes = [i for i in issues if i['issue_type'] == 'hreflang_invalid_code']
        assert len(invalid_codes) == 0
    
    def test_analyze_page_without_html(self, temp_db, sample_scan_id):
        """Test analyzing pages without HTML content."""
        module = HreflangModule(temp_db)
        
        pages = [
            {'url': 'https://example.com', 'html': None},
            {'url': 'https://example.com/page2'}
        ]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 0
    
    def test_severity_levels(self, temp_db, sample_scan_id):
        """Test that correct severity levels are assigned."""
        module = HreflangModule(temp_db)
        
        html = '''
        <html>
            <head>
                <link rel="alternate" hreflang="invalid" href="https://example.com/invalid">
            </head>
            <body>Content</body>
        </html>
        '''
        
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        # Invalid codes should be high severity
        invalid_issues = [i for i in issues if i['issue_type'] == 'hreflang_invalid_code']
        assert all(issue['severity'] == 'high' for issue in invalid_issues)