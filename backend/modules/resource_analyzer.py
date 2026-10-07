# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
Resource Analyzer Module

Analyzes and categorizes crawled resources by type (HTML, CSS, JS, images, etc.).
Provides statistics similar to Screaming Frog's resource breakdown.
"""

from typing import List, Dict
from urllib.parse import urlparse


class ResourceAnalyzer:
    """Analyzes and categorizes crawled resources by type."""
    
    def __init__(self):
        """Initialize the resource analyzer."""
        pass
    
    def analyze_resources(self, crawled_pages: List[Dict]) -> Dict:
        """
        Analyze and categorize all crawled resources by type.
        
        Args:
            crawled_pages: List of crawled resources from the crawler
        
        Returns:
            Dictionary with resource statistics:
            {
                'html_pages': int,         # HTML pages only
                'css_files': int,          # CSS stylesheets
                'js_files': int,           # JavaScript files
                'images': int,             # Images
                'other_resources': int,    # Other resources
                'total_resources': int,    # Total resources found
                'breakdown': {             # Detailed breakdown
                    'html': [...],
                    'css': [...],
                    'js': [...],
                    'images': [...],
                    'other': [...]
                }
            }
        """
        if not crawled_pages:
            return {
                'html_pages': 0,
                'css_files': 0,
                'js_files': 0,
                'images': 0,
                'other_resources': 0,
                'total_resources': 0,
                'breakdown': {
                    'html': [],
                    'css': [],
                    'js': [],
                    'images': [],
                    'other': []
                }
            }
        
        # Initialize counters and lists
        html_pages = []
        css_files = []
        js_files = []
        images = []
        other_resources = []
        
        for page in crawled_pages:
            url = page.get('url', '')
            resource_type = self._determine_resource_type(page, url)
            
            resource_info = {
                'url': url,
                'status': page.get('status', 0),
                'size': len(page.get('html', '')) if page.get('html') else 0
            }
            
            if resource_type == 'html':
                html_pages.append(resource_info)
            elif resource_type == 'css':
                css_files.append(resource_info)
            elif resource_type == 'js':
                js_files.append(resource_info)
            elif resource_type == 'image':
                images.append(resource_info)
            else:
                other_resources.append(resource_info)
        
        total_resources = len(crawled_pages)
        
        return {
            'html_pages': len(html_pages),
            'css_files': len(css_files),
            'js_files': len(js_files),
            'images': len(images),
            'other_resources': len(other_resources),
            'total_resources': total_resources,
            'breakdown': {
                'html': html_pages,
                'css': css_files,
                'js': js_files,
                'images': images,
                'other': other_resources
            }
        }
    
    def _determine_resource_type(self, page: Dict, url: str) -> str:
        """
        Determine the type of resource based on URL and content.
        
        Args:
            page: Page/resource dictionary
            url: Resource URL
        
        Returns:
            Resource type: 'html', 'css', 'js', 'image', 'other'
        """
        # Check if it's marked as a resource (not an HTML page)
        if page.get('is_resource'):
            # Determine type by URL extension
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            if path.endswith(('.css')):
                return 'css'
            elif path.endswith(('.js', '.mjs')):
                return 'js'
            elif path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico', '.bmp')):
                return 'image'
            else:
                return 'other'
        
        # Check if it has HTML content (indicates it's an HTML page)
        if page.get('html'):
            return 'html'
        
        # Determine type by URL extension
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        if path.endswith(('.html', '.htm', '.xhtml', '.php', '.asp', '.aspx')):
            return 'html'
        elif path.endswith(('.css')):
            return 'css'
        elif path.endswith(('.js', '.mjs')):
            return 'js'
        elif path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico', '.bmp')):
            return 'image'
        else:
            return 'other'
    
    def get_resource_percentages(self, analysis: Dict) -> Dict:
        """
        Calculate percentages for each resource type.
        
        Args:
            analysis: Resource analysis dictionary from analyze_resources()
        
        Returns:
            Dictionary with percentages for each resource type
        """
        total = analysis.get('total_resources', 0)
        
        if total == 0:
            return {
                'html': 0,
                'css': 0,
                'js': 0,
                'images': 0,
                'other': 0
            }
        
        return {
            'html': round((analysis['html_pages'] / total) * 100, 1),
            'css': round((analysis['css_files'] / total) * 100, 1),
            'js': round((analysis['js_files'] / total) * 100, 1),
            'images': round((analysis['images'] / total) * 100, 1),
            'other': round((analysis['other_resources'] / total) * 100, 1)
        }