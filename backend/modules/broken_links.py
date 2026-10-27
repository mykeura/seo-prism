# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

from typing import List, Dict, Set
from urllib.parse import urlparse
from core.url_utils import normalize_url
from database import Database


class BrokenLinksModule:
    """Module to detect broken links in crawled pages - focused on broken resources only."""
    
    IGNORED_DOMAINS = {
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
        
        'discord.com', 'discord.gg',
        'slack.com',
        'messenger.com',
        'viber.com',
        'wechat.com',
        'line.me',
        'skype.com',
        'zoom.us',
        
        'mailto:', 'tel:', 'callto:',
        'javascript:', 'data:',
        'amzn.to',  # Amazon affiliate links
        'app.box.com',  # Box file sharing
        'chromewebstore.google.com',  # Chrome Web Store
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
        if url.startswith(('mailto:', 'tel:', 'callto:', 'javascript:', 'data:')):
            return True
        
        try:
            parsed = urlparse(url)
            domain = parsed.hostname or ''
            
            for ignored_domain in self.IGNORED_DOMAINS:
                if domain == ignored_domain or domain.endswith('.' + ignored_domain):
                    return True
            
            if 'facebook.com/share' in url or 'twitter.com/share' in url:
                return True
            if 'linkedin.com/share' in url or 'linkedin.com/sharing' in url:
                return True
                
        except Exception:
            pass
        
        return False
    
    def analyze(self, scan_id: int, crawled_pages: List[Dict]) -> List[Dict]:
        """
        Analyze crawled pages for broken links and resources only.
        
        Args:
            scan_id: Scan ID
            crawled_pages: List of crawled page results
        
        Returns:
            List of broken link issues
        """
        issues = []
        
        url_status_map = {}
        for page in crawled_pages:
            url_status_map[page['url']] = page['status']
            # Links point at the requested URL; when it redirected, the
            # broken-health of the link is the status reached at the end of
            # the chain (e.g. /old -> 301 -> /missing 404).
            requested_url = page.get('requested_url')
            if requested_url:
                url_status_map[requested_url] = page.get('final_status', page['status'])
        
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
        
        # Check each resource. Crawled page URLs are normalized but resource
        # URLs are not, so normalize before the status-map lookup (and for
        # dedup); the original URL is kept for reporting.
        checked_resources: Set[str] = set()
        for resource in all_resources:
            resource_url = resource['url']
            normalized_url = normalize_url(resource_url)
            
            if normalized_url in checked_resources:
                continue
            checked_resources.add(normalized_url)
            
            if self._should_ignore_url(resource_url):
                continue
            
            if normalized_url in url_status_map:
                resource_status = url_status_map[normalized_url]
                
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
                    
                    self.db.add_issue(
                        scan_id=scan_id,
                        issue_type=issue_type,
                        url=resource_url,
                        source_page=resource['source'],
                        description=f"Broken {resource['type']} (HTTP {resource_status})",
                        severity=issue['severity']
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
            return 'high'
        elif status_code >= 400:
            return 'medium'
        else:
            return 'low'