# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 mykeura <mykeura@hotmail.com>

"""
Unit tests for report_generator module.
"""
import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path

from modules.report_generator import SEOReportGenerator


@pytest.fixture
def sample_results():
    """Sample scan results for testing."""
    return {
        'scan': {
            'id': 1,
            'url': 'https://example.com',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_pages': 10,
            'total_issues': 25
        },
        'issues': [
            {
                'id': 1,
                'issue_type': 'broken_links',
                'url': 'https://example.com/page1',
                'source_page': 'https://example.com/home',
                'description': 'Link returns 404 error',
                'severity': 'high'
            },
            {
                'id': 2,
                'issue_type': 'broken_links',
                'url': 'https://example.com/page2',
                'source_page': 'https://example.com/about',
                'description': 'Link returns 500 error',
                'severity': 'high'
            },
            {
                'id': 3,
                'issue_type': 'missing_title',
                'url': 'https://example.com/page3',
                'description': 'Page missing title tag',
                'severity': 'high'
            },
            {
                'id': 4,
                'issue_type': 'missing_description',
                'url': 'https://example.com/page4',
                'description': 'Page missing meta description',
                'severity': 'medium'
            },
            {
                'id': 5,
                'issue_type': 'title_too_long',
                'url': 'https://example.com/page5',
                'description': 'Title exceeds 60 characters',
                'severity': 'medium'
            },
            {
                'id': 6,
                'issue_type': 'duplicate_title',
                'url': 'https://example.com/page6',
                'description': 'Duplicate title found',
                'severity': 'medium'
            },
            {
                'id': 7,
                'issue_type': 'missing_alt_tag',
                'url': 'https://example.com/images/logo.png',
                'description': 'Image missing alt text',
                'severity': 'medium'
            },
            {
                'id': 8,
                'issue_type': 'missing_h1',
                'url': 'https://example.com/page7',
                'description': 'Page missing H1 header',
                'severity': 'high'
            },
            {
                'id': 9,
                'issue_type': 'missing_sitemap',
                'url': 'https://example.com/sitemap.xml',
                'description': 'Sitemap.xml not found',
                'severity': 'high'
            },
            {
                'id': 10,
                'issue_type': 'thin_content',
                'url': 'https://example.com/page8',
                'description': 'Page has thin content',
                'severity': 'high'
            },
        ],
        'pages': [],
        'seo_grade': {
            'score': 65,
            'grade': 'D',
            'breakdown': {
                'high': 5,
                'medium': 4,
                'low': 1,
                'total': 10
            }
        },
        'resource_analysis': {
            'html_pages': 10,
            'css_files': 3,
            'js_files': 5,
            'images': 20,
            'other_resources': 8,
            'total_resources': 46
        }
    }


@pytest.fixture
def sample_results_perfect():
    """Sample scan results with perfect grade."""
    return {
        'scan': {
            'id': 1,
            'url': 'https://perfect.com',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_pages': 5,
            'total_issues': 0
        },
        'issues': [],
        'pages': [],
        'seo_grade': {
            'score': 100,
            'grade': 'A',
            'breakdown': {
                'high': 0,
                'medium': 0,
                'low': 0,
                'total': 0
            }
        },
        'resource_analysis': {
            'html_pages': 5,
            'css_files': 2,
            'js_files': 3,
            'images': 10,
            'other_resources': 4,
            'total_resources': 24
        }
    }


@pytest.fixture
def sample_results_failing():
    """Sample scan results with failing grade."""
    return {
        'scan': {
            'id': 1,
            'url': 'https://failing.com',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_pages': 20,
            'total_issues': 150
        },
        'issues': [
            {
                'id': i,
                'issue_type': 'broken_links',
                'url': f'https://failing.com/page{i}',
                'source_page': 'https://failing.com/home',
                'description': 'Link returns 404 error',
                'severity': 'high'
            } for i in range(50)
        ] + [
            {
                'id': i + 50,
                'issue_type': 'missing_title',
                'url': f'https://failing.com/page{i + 50}',
                'description': 'Page missing title tag',
                'severity': 'high'
            } for i in range(50)
        ] + [
            {
                'id': i + 100,
                'issue_type': 'missing_description',
                'url': f'https://failing.com/page{i + 100}',
                'description': 'Page missing meta description',
                'severity': 'medium'
            } for i in range(50)
        ],
        'pages': [],
        'seo_grade': {
            'score': 0,
            'grade': 'F',
            'breakdown': {
                'high': 100,
                'medium': 50,
                'low': 0,
                'total': 150
            }
        },
        'resource_analysis': {
            'html_pages': 20,
            'css_files': 5,
            'js_files': 10,
            'images': 50,
            'other_resources': 20,
            'total_resources': 105
        }
    }


class TestSEOReportGenerator:
    """Tests for SEOReportGenerator class."""
    
    def test_generate_report_english(self, sample_results):
        """Test generating report in English."""
        generator = SEOReportGenerator()
        
        fd, path = tempfile.mkstemp(suffix='.pptx')
        os.close(fd)
        
        try:
            result_path = generator.generate_report(sample_results, path, 'en')
            
            assert result_path == path
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0
        finally:
            if os.path.exists(path):
                os.unlink(path)
    
    def test_generate_report_spanish(self, sample_results):
        """Test generating report in Spanish."""
        generator = SEOReportGenerator()
        
        fd, path = tempfile.mkstemp(suffix='.pptx')
        os.close(fd)
        
        try:
            result_path = generator.generate_report(sample_results, path, 'es')
            
            assert result_path == path
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0
        finally:
            if os.path.exists(path):
                os.unlink(path)
    
    def test_generate_report_perfect_grade(self, sample_results_perfect):
        """Test generating report with perfect grade (A)."""
        generator = SEOReportGenerator()
        
        fd, path = tempfile.mkstemp(suffix='.pptx')
        os.close(fd)
        
        try:
            result_path = generator.generate_report(sample_results_perfect, path, 'en')
            
            assert result_path == path
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0
        finally:
            if os.path.exists(path):
                os.unlink(path)
    
    def test_generate_report_failing_grade(self, sample_results_failing):
        """Test generating report with failing grade (F)."""
        generator = SEOReportGenerator()
        
        fd, path = tempfile.mkstemp(suffix='.pptx')
        os.close(fd)
        
        try:
            result_path = generator.generate_report(sample_results_failing, path, 'en')
            
            assert result_path == path
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0
        finally:
            if os.path.exists(path):
                os.unlink(path)
    
    def test_default_theme_colors(self):
        """Test that default theme colors are set correctly."""
        generator = SEOReportGenerator()
        
        assert 'primary' in generator.theme
        assert 'secondary' in generator.theme
        assert 'accent' in generator.theme
        assert 'success' in generator.theme
        assert 'warning' in generator.theme
        assert 'danger' in generator.theme
        assert 'background' in generator.theme
        assert 'text' in generator.theme
        assert 'text_light' in generator.theme
    
    def test_custom_theme_colors(self):
        """Test that custom theme colors can be set."""
        custom_theme = {
            'primary': (255, 0, 0),
            'accent': (0, 255, 0)
        }
        generator = SEOReportGenerator(custom_theme=custom_theme)
        
        assert generator.theme['primary'] == (255, 0, 0)
        assert generator.theme['accent'] == (0, 255, 0)
        # Default colors should still be present
        assert 'success' in generator.theme
        assert 'warning' in generator.theme
    
    def test_generate_report_with_empty_issues(self, sample_results_perfect):
        """Test generating report with no issues."""
        generator = SEOReportGenerator()
        
        fd, path = tempfile.mkstemp(suffix='.pptx')
        os.close(fd)
        
        try:
            result_path = generator.generate_report(sample_results_perfect, path, 'en')
            
            assert result_path == path
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0
        finally:
            if os.path.exists(path):
                os.unlink(path)
    
    def test_generate_report_with_many_issues(self, sample_results_failing):
        """Test generating report with many issues (extensive report)."""
        generator = SEOReportGenerator()
        
        fd, path = tempfile.mkstemp(suffix='.pptx')
        os.close(fd)
        
        try:
            result_path = generator.generate_report(sample_results_failing, path, 'en')
            
            assert result_path == path
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0
            # Report with many issues should be larger
            size = os.path.getsize(path)
            assert size > 10000  # At least 10KB
        finally:
            if os.path.exists(path):
                os.unlink(path)
    
    def test_generate_report_different_grades(self):
        """Test generating reports with different grades."""
        generator = SEOReportGenerator()
        
        grades = [
            {'score': 95, 'grade': 'A'},
            {'score': 85, 'grade': 'B'},
            {'score': 75, 'grade': 'C'},
            {'score': 65, 'grade': 'D'},
            {'score': 45, 'grade': 'F'}
        ]
        
        for grade_data in grades:
            results = {
                'scan': {
                    'id': 1,
                    'url': 'https://example.com',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_pages': 10,
                    'total_issues': 10
                },
                'issues': [
                    {
                        'id': i,
                        'issue_type': 'broken_links',
                        'url': f'https://example.com/page{i}',
                        'description': 'Test issue',
                        'severity': 'medium'
                    } for i in range(10)
                ],
                'pages': [],
                'seo_grade': {
                    'score': grade_data['score'],
                    'grade': grade_data['grade'],
                    'breakdown': {
                        'high': 0,
                        'medium': 10,
                        'low': 0,
                        'total': 10
                    }
                },
                'resource_analysis': {
                    'html_pages': 10,
                    'css_files': 2,
                    'js_files': 3,
                    'images': 10,
                    'other_resources': 5,
                    'total_resources': 30
                }
            }
            
            fd, path = tempfile.mkstemp(suffix='.pptx')
            os.close(fd)
            
            try:
                result_path = generator.generate_report(results, path, 'en')
                assert result_path == path
                assert os.path.exists(path)
                assert os.path.getsize(path) > 0
            finally:
                if os.path.exists(path):
                    os.unlink(path)
    
    def test_generate_report_file_not_writable(self, sample_results):
        """Test handling of file write errors."""
        generator = SEOReportGenerator()
        
        # Use a path that doesn't exist and can't be created
        invalid_path = '/root/nonexistent_directory/test.pptx'
        
        with pytest.raises(Exception):
            generator.generate_report(sample_results, invalid_path, 'en')