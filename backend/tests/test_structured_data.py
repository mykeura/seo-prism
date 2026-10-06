# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
Unit tests for structured_data module.
"""
import pytest
from modules.structured_data import StructuredDataModule


class TestStructuredDataModule:
    """Tests for StructuredDataModule class."""
    
    def test_analyze_missing_structured_data(self, temp_db, sample_scan_id):
        """Test detecting missing structured data."""
        module = StructuredDataModule(temp_db)
        
        html = '<html><head><title>Page</title></head><body>Content</body></html>'
        pages = [{'url': 'https://example.com', 'html': html}]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'missing_structured_data'
        assert issues[0]['severity'] == 'medium'
    
    def test_analyze_valid_json_ld(self, temp_db, sample_scan_id):
        """Test analyzing valid JSON-LD."""
        module = StructuredDataModule(temp_db)
        
        html = '''
        <html>
            <head>
                <title>Page</title>
                <script type="application/ld+json">
                {
                    "@context": "https://schema.org",
                    "@type": "Article",
                    "headline": "Test Article",
                    "author": {"@type": "Person", "name": "John Doe"},
                    "datePublished": "2024-01-01",
                    "publisher": {"@type": "Organization", "name": "Example"}
                }
                </script>
            </head>
            <body>Content</body>
        </html>
        '''
        pages = [{'url': 'https://example.com', 'html': html}]
        
        issues = module.analyze(sample_scan_id, pages)
        
        # Should not report missing structured data
        missing_issues = [i for i in issues if i['issue_type'] == 'missing_structured_data']
        assert len(missing_issues) == 0
    
    def test_analyze_json_ld_invalid_json(self, temp_db, sample_scan_id):
        """Test detecting invalid JSON in JSON-LD."""
        module = StructuredDataModule(temp_db)
        
        html = '''
        <html>
            <head>
                <title>Page</title>
                <script type="application/ld+json">
                {
                    "@context": "https://schema.org",
                    "@type": "Article",
                    "headline": "Test Article",
                    "author": {"@type": "Person", "name": "John Doe"},
                    "datePublished": "2024-01-01",
                    "publisher": {"@type": "Organization", "name": "Example"
                </script>
            </head>
            <body>Content</body>
        </html>
        '''
        pages = [{'url': 'https://example.com', 'html': html}]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) >= 1
        invalid_json = [i for i in issues if i['issue_type'] == 'json_ld_invalid_json']
        assert len(invalid_json) >= 1
    
    def test_analyze_json_ld_missing_type(self, temp_db, sample_scan_id):
        """Test detecting JSON-LD without @type."""
        module = StructuredDataModule(temp_db)
        
        html = '''
        <html>
            <head>
                <title>Page</title>
                <script type="application/ld+json">
                {
                    "@context": "https://schema.org",
                    "headline": "Test Article"
                }
                </script>
            </head>
            <body>Content</body>
        </html>
        '''
        pages = [{'url': 'https://example.com', 'html': html}]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) >= 1
        missing_type = [i for i in issues if i['issue_type'] == 'json_ld_missing_type']
        assert len(missing_type) >= 1
    
    def test_analyze_json_ld_unknown_type(self, temp_db, sample_scan_id):
        """Test detecting unknown schema type."""
        module = StructuredDataModule(temp_db)
        
        html = '''
        <html>
            <head>
                <title>Page</title>
                <script type="application/ld+json">
                {
                    "@context": "https://schema.org",
                    "@type": "UnknownType",
                    "headline": "Test"
                }
                </script>
            </head>
            <body>Content</body>
        </html>
        '''
        pages = [{'url': 'https://example.com', 'html': html}]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) >= 1
        unknown_type = [i for i in issues if i['issue_type'] == 'json_ld_unknown_type']
        assert len(unknown_type) >= 1
    
    def test_analyze_json_ld_missing_properties(self, temp_db, sample_scan_id):
        """Test detecting missing required properties."""
        module = StructuredDataModule(temp_db)
        
        html = '''
        <html>
            <head>
                <title>Page</title>
                <script type="application/ld+json">
                {
                    "@context": "https://schema.org",
                    "@type": "Article",
                    "headline": "Test"
                }
                </script>
            </head>
            <body>Content</body>
        </html>
        '''
        pages = [{'url': 'https://example.com', 'html': html}]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) >= 1
        missing_props = [i for i in issues if i['issue_type'] == 'json_ld_missing_properties']
        assert len(missing_props) >= 1
    
    def test_analyze_json_ld_short_headline(self, temp_db, sample_scan_id):
        """Test detecting short headline in Article."""
        module = StructuredDataModule(temp_db)
        
        html = '''
        <html>
            <head>
                <title>Page</title>
                <script type="application/ld+json">
                {
                    "@context": "https://schema.org",
                    "@type": "Article",
                    "headline": "Short",
                    "author": {"@type": "Person", "name": "John Doe"},
                    "datePublished": "2024-01-01",
                    "publisher": {"@type": "Organization", "name": "Example"}
                }
                </script>
            </head>
            <body>Content</body>
        </html>
        '''
        pages = [{'url': 'https://example.com', 'html': html}]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) >= 1
        short_headline = [i for i in issues if i['issue_type'] == 'json_ld_short_headline']
        assert len(short_headline) >= 1
    
    def test_analyze_microdata_missing_type(self, temp_db, sample_scan_id):
        """Test detecting Microdata without itemtype."""
        module = StructuredDataModule(temp_db)
        
        html = '''
        <html>
            <head><title>Page</title></head>
            <body>
                <div itemscope itemprop="name">Test</div>
            </body>
        </html>
        '''
        pages = [{'url': 'https://example.com', 'html': html}]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) >= 1
        missing_type = [i for i in issues if i['issue_type'] == 'microdata_missing_type']
        assert len(missing_type) >= 1
    
    def test_analyze_microdata_unknown_type(self, temp_db, sample_scan_id):
        """Test detecting unknown Microdata type."""
        module = StructuredDataModule(temp_db)
        
        html = '''
        <html>
            <head><title>Page</title></head>
            <body>
                <div itemscope itemtype="https://schema.org/UnknownType">
                    <span itemprop="name">Test</span>
                </div>
            </body>
        </html>
        '''
        pages = [{'url': 'https://example.com', 'html': html}]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) >= 1
        unknown_type = [i for i in issues if i['issue_type'] == 'microdata_unknown_type']
        assert len(unknown_type) >= 1
    
    def test_analyze_rdfa_unknown_type(self, temp_db, sample_scan_id):
        """Test detecting unknown RDFa type."""
        module = StructuredDataModule(temp_db)
        
        html = '''
        <html>
            <head><title>Page</title></head>
            <body>
                <div typeof="schema:UnknownType">
                    <span property="schema:name">Test</span>
                </div>
            </body>
        </html>
        '''
        pages = [{'url': 'https://example.com', 'html': html}]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) >= 1
        unknown_type = [i for i in issues if i['issue_type'] == 'rdfa_unknown_type']
        assert len(unknown_type) >= 1
    
    def test_analyze_json_ld_graph(self, temp_db, sample_scan_id):
        """Test analyzing JSON-LD with @graph."""
        module = StructuredDataModule(temp_db)
        
        html = '''
        <html>
            <head>
                <title>Page</title>
                <script type="application/ld+json">
                {
                    "@context": "https://schema.org",
                    "@graph": [
                        {
                            "@type": "Article",
                            "headline": "Test Article"
                        },
                        {
                            "@type": "Organization",
                            "name": "Example"
                        }
                    ]
                }
                </script>
            </head>
            <body>Content</body>
        </html>
        '''
        pages = [{'url': 'https://example.com', 'html': html}]
        
        issues = module.analyze(sample_scan_id, pages)
        
        # Should not report missing structured data
        missing_issues = [i for i in issues if i['issue_type'] == 'missing_structured_data']
        assert len(missing_issues) == 0
    
    def test_analyze_page_without_html(self, temp_db, sample_scan_id):
        """Test analyzing pages without HTML content."""
        module = StructuredDataModule(temp_db)
        
        pages = [
            {'url': 'https://example.com', 'html': None},
            {'url': 'https://example.com/page2'}
        ]
        
        issues = module.analyze(sample_scan_id, pages)
        
        assert len(issues) == 0
    
    def test_severity_levels(self, temp_db, sample_scan_id):
        """Test that correct severity levels are assigned."""
        module = StructuredDataModule(temp_db)
        
        html = '''
        <html>
            <head>
                <title>Page</title>
                <script type="application/ld+json">
                {
                    "@context": "https://schema.org",
                    "@type": "Article",
                    "headline": "Short"
                }
                </script>
            </head>
            <body>Content</body>
        </html>
        '''
        pages = [{'url': 'https://example.com', 'html': html}]
        issues = module.analyze(sample_scan_id, pages)
        
        # Missing properties should be high severity
        missing_props = [i for i in issues if i['issue_type'] == 'json_ld_missing_properties']
        assert all(issue['severity'] == 'high' for issue in missing_props)
        
        # Short headline should be medium severity
        short_headline = [i for i in issues if i['issue_type'] == 'json_ld_short_headline']
        assert all(issue['severity'] == 'medium' for issue in short_headline)