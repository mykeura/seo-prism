# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 mykeura <mykeura@hotmail.com>

"""
Unit tests for resource_analyzer module.
"""
import pytest
from modules.resource_analyzer import ResourceAnalyzer


class TestResourceAnalyzer:
    """Tests for ResourceAnalyzer class."""
    
    def test_analyze_resources_empty(self):
        """Test analyzing empty resources list."""
        analyzer = ResourceAnalyzer()
        result = analyzer.analyze_resources([])
        
        assert result['html_pages'] == 0
        assert result['css_files'] == 0
        assert result['js_files'] == 0
        assert result['images'] == 0
        assert result['other_resources'] == 0
        assert result['total_resources'] == 0
        assert len(result['breakdown']['html']) == 0
        assert len(result['breakdown']['css']) == 0
        assert len(result['breakdown']['js']) == 0
        assert len(result['breakdown']['images']) == 0
        assert len(result['breakdown']['other']) == 0
    
    def test_analyze_resources_html_only(self):
        """Test analyzing HTML pages only."""
        analyzer = ResourceAnalyzer()
        resources = [
            {
                'url': 'http://example.com/page1',
                'status': 200,
                'html': '<html><body>Page 1</body></html>'
            },
            {
                'url': 'http://example.com/page2',
                'status': 200,
                'html': '<html><body>Page 2</body></html>'
            }
        ]
        result = analyzer.analyze_resources(resources)
        
        assert result['html_pages'] == 2
        assert result['css_files'] == 0
        assert result['js_files'] == 0
        assert result['images'] == 0
        assert result['total_resources'] == 2
        assert len(result['breakdown']['html']) == 2
    
    def test_analyze_resources_css_files(self):
        """Test analyzing CSS files."""
        analyzer = ResourceAnalyzer()
        resources = [
            {
                'url': 'http://example.com/style.css',
                'status': 200,
                'is_resource': True
            }
        ]
        result = analyzer.analyze_resources(resources)
        
        assert result['css_files'] == 1
        assert result['html_pages'] == 0
        assert result['total_resources'] == 1
    
    def test_analyze_resources_js_files(self):
        """Test analyzing JavaScript files."""
        analyzer = ResourceAnalyzer()
        resources = [
            {
                'url': 'http://example.com/script.js',
                'status': 200,
                'is_resource': True
            },
            {
                'url': 'http://example.com/module.mjs',
                'status': 200,
                'is_resource': True
            }
        ]
        result = analyzer.analyze_resources(resources)
        
        assert result['js_files'] == 2
        assert result['html_pages'] == 0
        assert result['total_resources'] == 2
    
    def test_analyze_resources_images(self):
        """Test analyzing image files."""
        analyzer = ResourceAnalyzer()
        resources = [
            {'url': 'http://example.com/image.jpg', 'status': 200, 'is_resource': True},
            {'url': 'http://example.com/image.png', 'status': 200, 'is_resource': True},
            {'url': 'http://example.com/image.gif', 'status': 200, 'is_resource': True},
            {'url': 'http://example.com/image.svg', 'status': 200, 'is_resource': True},
            {'url': 'http://example.com/image.webp', 'status': 200, 'is_resource': True},
            {'url': 'http://example.com/image.ico', 'status': 200, 'is_resource': True},
        ]
        result = analyzer.analyze_resources(resources)
        
        assert result['images'] == 6
        assert result['total_resources'] == 6
    
    def test_analyze_resources_mixed(self):
        """Test analyzing mixed resource types."""
        analyzer = ResourceAnalyzer()
        resources = [
            {'url': 'http://example.com/', 'status': 200, 'html': '<html></html>'},
            {'url': 'http://example.com/style.css', 'status': 200, 'is_resource': True},
            {'url': 'http://example.com/script.js', 'status': 200, 'is_resource': True},
            {'url': 'http://example.com/image.jpg', 'status': 200, 'is_resource': True},
            {'url': 'http://example.com/unknown.pdf', 'status': 200, 'is_resource': True},
        ]
        result = analyzer.analyze_resources(resources)
        
        assert result['html_pages'] == 1
        assert result['css_files'] == 1
        assert result['js_files'] == 1
        assert result['images'] == 1
        assert result['other_resources'] == 1
        assert result['total_resources'] == 5
    
    def test_determine_resource_type_html_by_content(self):
        """Test determining HTML type by content."""
        analyzer = ResourceAnalyzer()
        page = {
            'url': 'http://example.com/page',
            'html': '<html><body>Content</body></html>'
        }
        resource_type = analyzer._determine_resource_type(page, 'http://example.com/page')
        
        assert resource_type == 'html'
    
    def test_determine_resource_type_html_by_extension(self):
        """Test determining HTML type by extension."""
        analyzer = ResourceAnalyzer()
        page = {'url': 'http://example.com/page.html', 'is_resource': False}
        resource_type = analyzer._determine_resource_type(page, 'http://example.com/page.html')
        
        assert resource_type == 'html'
    
    def test_determine_resource_type_css(self):
        """Test determining CSS type."""
        analyzer = ResourceAnalyzer()
        page = {'url': 'http://example.com/style.css', 'is_resource': True}
        resource_type = analyzer._determine_resource_type(page, 'http://example.com/style.css')
        
        assert resource_type == 'css'
    
    def test_determine_resource_type_js(self):
        """Test determining JavaScript type."""
        analyzer = ResourceAnalyzer()
        page = {'url': 'http://example.com/script.js', 'is_resource': True}
        resource_type = analyzer._determine_resource_type(page, 'http://example.com/script.js')
        
        assert resource_type == 'js'
    
    def test_determine_resource_type_image(self):
        """Test determining image type."""
        analyzer = ResourceAnalyzer()
        page = {'url': 'http://example.com/image.jpg', 'is_resource': True}
        resource_type = analyzer._determine_resource_type(page, 'http://example.com/image.jpg')
        
        assert resource_type == 'image'
    
    def test_determine_resource_type_other(self):
        """Test determining other resource type."""
        analyzer = ResourceAnalyzer()
        page = {'url': 'http://example.com/file.pdf', 'is_resource': True}
        resource_type = analyzer._determine_resource_type(page, 'http://example.com/file.pdf')
        
        assert resource_type == 'other'
    
    def test_get_resource_percentages(self):
        """Test calculating resource percentages."""
        analyzer = ResourceAnalyzer()
        analysis = {
            'html_pages': 2,
            'css_files': 1,
            'js_files': 1,
            'images': 1,
            'other_resources': 1,
            'total_resources': 6
        }
        percentages = analyzer.get_resource_percentages(analysis)
        
        assert percentages['html'] == 33.3
        assert percentages['css'] == 16.7
        assert percentages['js'] == 16.7
        assert percentages['images'] == 16.7
        assert percentages['other'] == 16.7
    
    def test_get_resource_percentages_zero_total(self):
        """Test calculating percentages with zero total."""
        analyzer = ResourceAnalyzer()
        analysis = {
            'html_pages': 0,
            'css_files': 0,
            'js_files': 0,
            'images': 0,
            'other_resources': 0,
            'total_resources': 0
        }
        percentages = analyzer.get_resource_percentages(analysis)
        
        assert percentages['html'] == 0
        assert percentages['css'] == 0
        assert percentages['js'] == 0
        assert percentages['images'] == 0
        assert percentages['other'] == 0
    
    def test_resource_info_includes_size(self):
        """Test that resource info includes size calculation."""
        analyzer = ResourceAnalyzer()
        html_content = '<html><body>Test content</body></html>'
        resources = [
            {'url': 'http://example.com/', 'status': 200, 'html': html_content}
        ]
        result = analyzer.analyze_resources(resources)
        
        assert len(result['breakdown']['html']) == 1
        assert result['breakdown']['html'][0]['size'] == len(html_content)
        assert result['breakdown']['html'][0]['url'] == 'http://example.com/'
        assert result['breakdown']['html'][0]['status'] == 200