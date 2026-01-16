from typing import List, Dict, Set
from database import Database


class BrokenLinksModule:
    """Module to detect broken links in crawled pages."""
    
    def __init__(self, db: Database):
        """
        Initialize the Broken Links module.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def analyze(self, scan_id: int, crawled_pages: List[Dict]) -> List[Dict]:
        """
        Analyze crawled pages for broken links and resources.
        
        Args:
            scan_id: Scan ID
            crawled_pages: List of crawled page results
        
        Returns:
            List of broken link issues
        """
        issues = []
        
        # Create a map of URLs to their status codes
        url_status_map = {}
        for page in crawled_pages:
            url_status_map[page['url']] = page['status']
        
        # Collect all resources from all pages
        all_resources = []
        for page in crawled_pages:
            page_url = page['url']
            resources = page.get('resources', [])
            
            for resource in resources:
                all_resources.append({
                    'url': resource['url'],
                    'type': resource['type'],
                    'source': page_url
                })
        
        # Check each resource
        checked_resources: Set[str] = set()
        for resource in all_resources:
            resource_url = resource['url']
            
            # Skip if already checked
            if resource_url in checked_resources:
                continue
            checked_resources.add(resource_url)
            
            # Check if resource URL exists in our crawled pages
            if resource_url in url_status_map:
                resource_status = url_status_map[resource_url]
                
                # Mark as broken if status >= 400
                if resource_status >= 400:
                    issue_type = self._get_issue_type(resource['type'])
                    issue = {
                        'issue_type': issue_type,
                        'url': resource_url,
                        'source_page': resource['source'],
                        'description': f"Broken {resource['type']} (HTTP {resource_status})",
                        'severity': self._get_severity(resource_status)
                    }
                    issues.append(issue)
                    
                    # Add to database
                    self.db.add_issue(
                        scan_id=scan_id,
                        issue_type=issue_type,
                        url=resource_url,
                        source_page=resource['source'],
                        description=f"Broken {resource['type']} (HTTP {resource_status})",
                        severity=issue['severity']
                    )
            else:
                # Resource was not crawled, mark as potentially broken
                issue_type = self._get_issue_type(resource['type'])
                issue = {
                    'issue_type': issue_type,
                    'url': resource_url,
                    'source_page': resource['source'],
                    'description': f"Uncrawled {resource['type']} (not verified)",
                    'severity': 'low'
                }
                issues.append(issue)
                
                # Add to database
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type=issue_type,
                    url=resource_url,
                    source_page=resource['source'],
                    description=f"Uncrawled {resource['type']} (not verified)",
                    severity='low'
                )
        
        return issues
    
    def _get_issue_type(self, resource_type: str) -> str:
        """
        Map resource type to issue type.
        
        Args:
            resource_type: Type of resource (anchor, image, script, link, etc.)
        
        Returns:
            Issue type string
        """
        type_mapping = {
            'anchor': 'broken_link',
            'image': 'broken_image',
            'script': 'broken_script',
            'stylesheet': 'broken_stylesheet',
            'link': 'broken_link'
        }
        return type_mapping.get(resource_type, 'broken_resource')
    
    def _get_severity(self, status_code: int) -> str:
        """
        Determine severity based on HTTP status code.
        
        Args:
            status_code: HTTP status code
        
        Returns:
            Severity level (low/medium/high)
        """
        if status_code >= 500:
            return 'high'  # Server errors
        elif status_code >= 400:
            return 'medium'  # Client errors
        else:
            return 'low'