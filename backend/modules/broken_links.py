from typing import List, Dict, Set
from urllib.parse import urlparse
from database import Database


class BrokenLinksModule:
    """Module to detect broken links in crawled pages."""
    
    # Social media and messaging services to ignore
    IGNORED_DOMAINS = {
        # Social Media
        'facebook.com', 'fb.com', 'facebook.net',
        'twitter.com', 'x.com', 't.co',
        'instagram.com', 'instagr.am',
        'linkedin.com', 'lnkd.in',
        'youtube.com', 'youtu.be',
        'tiktok.com',
        'pinterest.com',
        'snapchat.com',
        'reddit.com', 'redd.it',
        'tumblr.com',
        'whatsapp.com', 'wa.me',
        'telegram.org', 't.me',
        
        # Messaging Services
        'discord.com', 'discord.gg',
        'slack.com',
        'messenger.com',
        'viber.com',
        'wechat.com',
        'line.me',
        'skype.com',
        'zoom.us',
        
        # Other External Services
        'mailto:', 'tel:', 'callto:',
        'javascript:', 'data:',
        'amzn.to',  # Amazon affiliate links
    }
    
    def __init__(self, db: Database):
        """
        Initialize the Broken Links module.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def _should_ignore_url(self, url: str) -> bool:
        """
        Check if a URL should be ignored (social media, messaging, etc.)
        
        Args:
            url: URL to check
        
        Returns:
            True if URL should be ignored, False otherwise
        """
        # Check for protocol-based ignores
        if url.startswith(('mailto:', 'tel:', 'callto:', 'javascript:', 'data:')):
            return True
        
        # Parse URL
        try:
            parsed = urlparse(url)
            domain = parsed.hostname or ''
            
            # Check if domain is in ignored list
            for ignored_domain in self.IGNORED_DOMAINS:
                if domain == ignored_domain or domain.endswith('.' + ignored_domain):
                    return True
            
            # Check for common social media patterns
            if 'facebook.com/share' in url or 'twitter.com/share' in url:
                return True
            if 'linkedin.com/share' in url or 'linkedin.com/sharing' in url:
                return True
                
        except Exception:
            pass
        
        return False
    
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
            
            # Skip if URL should be ignored
            if self._should_ignore_url(resource_url):
                continue
            
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
            # Resources not in url_status_map were not verified by crawler
            # This should not happen with the new crawler logic that verifies all links
            # Keeping this as a safety net for any edge cases
        
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