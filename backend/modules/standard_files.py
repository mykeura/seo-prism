import asyncio
import aiohttp
from typing import List, Dict
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from database import Database


class StandardFilesModule:
    """Module to detect standard web files: robots.txt, sitemap.xml, security.txt"""
    
    def __init__(self, db: Database):
        """
        Initialize the Standard Files module.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    async def analyze(self, scan_id: int, base_url: str) -> List[Dict]:
        """
        Analyze website for standard files.
        
        Args:
            scan_id: Scan ID
            base_url: Base URL of the website
        
        Returns:
            List of standard files found
        """
        issues = []
        
        # Parse base URL to get domain and scheme
        try:
            parsed = urlparse(base_url)
            scheme = parsed.scheme or 'https'
            domain = parsed.hostname
            port = parsed.port
            
            if not domain:
                return issues
            
            # Include port if it's not the default for the scheme
            if port and ((scheme == 'http' and port != 80) or (scheme == 'https' and port != 443)):
                base_domain = f"{scheme}://{domain}:{port}"
            else:
                base_domain = f"{scheme}://{domain}"
            
        except Exception:
            return issues
        
        # Check for standard files
        async with aiohttp.ClientSession() as session:
            # Check robots.txt
            robots_url = f"{base_domain}/robots.txt"
            robots_found = await self._check_file_with_fallback(session, robots_url)
            if robots_found:
                issue = {
                    'issue_type': 'robots_txt_found',
                    'url': robots_url,
                    'source_page': base_url,
                    'description': 'robots.txt file found',
                    'severity': 'info'
                }
                issues.append(issue)
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='robots_txt_found',
                    url=robots_url,
                    source_page=base_url,
                    description='robots.txt file found',
                    severity='info'
                )
            else:
                # Report missing robots.txt as a low severity issue
                issue = {
                    'issue_type': 'missing_robots_txt',
                    'url': base_url,
                    'source_page': base_url,
                    'description': 'robots.txt file not found - recommended for SEO',
                    'severity': 'low'
                }
                issues.append(issue)
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='missing_robots_txt',
                    url=base_url,
                    source_page=base_url,
                    description='robots.txt file not found - recommended for SEO',
                    severity='low'
                )
            
            # Check security.txt
            security_url = f"{base_domain}/.well-known/security.txt"
            security_alt_url = f"{base_domain}/security.txt"  # Alternative location
            
            security_found = await self._check_file_with_fallback(session, security_url)
            if not security_found:
                security_found = await self._check_file_with_fallback(session, security_alt_url)
            
            if security_found:
                found_url = security_url if await self._check_file_with_fallback(session, security_url) else security_alt_url
                issue = {
                    'issue_type': 'security_txt_found',
                    'url': found_url,
                    'source_page': base_url,
                    'description': 'security.txt file found',
                    'severity': 'info'
                }
                issues.append(issue)
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='security_txt_found',
                    url=found_url,
                    source_page=base_url,
                    description='security.txt file found',
                    severity='info'
                )
            else:
                # Report missing security.txt as info (not required)
                issue = {
                    'issue_type': 'missing_security_txt',
                    'url': base_url,
                    'source_page': base_url,
                    'description': 'security.txt file not found - optional but recommended for security',
                    'severity': 'info'
                }
                issues.append(issue)
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='missing_security_txt',
                    url=base_url,
                    source_page=base_url,
                    description='security.txt file not found - optional but recommended for security',
                    severity='info'
                )
            
            # Check for sitemaps
            sitemaps = await self._find_sitemaps(session, base_url, base_domain)
            if sitemaps:
                for sitemap_url in sitemaps:
                    issue = {
                        'issue_type': 'sitemap_found',
                        'url': sitemap_url,
                        'source_page': base_url,
                        'description': 'sitemap file found',
                        'severity': 'info'
                    }
                    issues.append(issue)
                    self.db.add_issue(
                        scan_id=scan_id,
                        issue_type='sitemap_found',
                        url=sitemap_url,
                        source_page=base_url,
                        description='sitemap file found',
                        severity='info'
                    )
            else:
                # Report missing sitemap as a medium severity issue
                issue = {
                    'issue_type': 'missing_sitemap',
                    'url': base_url,
                    'source_page': base_url,
                    'description': 'No sitemap found - highly recommended for SEO',
                    'severity': 'medium'
                }
                issues.append(issue)
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='missing_sitemap',
                    url=base_url,
                    source_page=base_url,
                    description='No sitemap found - highly recommended for SEO',
                    severity='medium'
                )
        
        return issues
    
    async def _check_file_with_fallback(self, session: aiohttp.ClientSession, url: str) -> bool:
        """
        Check if a file exists at the given URL with fallback from HEAD to GET request.
        
        Args:
            session: aiohttp session
            url: URL to check
        
        Returns:
            True if file exists, False otherwise
        """
        try:
            # Try HEAD request first
            async with session.head(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass
        
        try:
            # Fallback to GET request and check status
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                return response.status == 200
        except Exception:
            return False
    
    async def _find_sitemaps(self, session: aiohttp.ClientSession, base_url: str, base_domain: str) -> List[str]:
        """
        Find all sitemap files for the website.
        
        Args:
            session: aiohttp session
            base_url: Base URL of the website
            base_domain: Base domain (scheme://domain)
        
        Returns:
            List of sitemap URLs
        """
        sitemaps = []
        
        # Common sitemap filenames to check (prioritize Astro format)
        common_sitemap_names = [
            'sitemap-index.xml',  # Astro format (highest priority)
            'sitemap_index.xml',  # Alternative format
            'sitemap.xml',
            'sitemap_index.xml.gz',
            'sitemap.xml.gz',
            'sitemap1.xml',
            'sitemap1.xml.gz',
            'posts-sitemap.xml',
            'page-sitemap.xml'
        ]
        
        # Method 1: Check common sitemap locations
        for sitemap_name in common_sitemap_names:
            sitemap_url = f"{base_domain}/{sitemap_name}"
            if await self._check_file_with_fallback(session, sitemap_url):
                if sitemap_url not in sitemaps:
                    sitemaps.append(sitemap_url)
        
        # Method 2: Check robots.txt for sitemap references
        robots_url = f"{base_domain}/robots.txt"
        try:
            async with session.get(robots_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    content = await response.text()
                    for line in content.split('\n'):
                        line = line.strip()
                        if line.lower().startswith('sitemap:'):
                            sitemap_url = line.split(':', 1)[1].strip()
                            if sitemap_url:
                                # Convert relative URLs to absolute if needed
                                if sitemap_url.startswith('/'):
                                    sitemap_url = f"{base_domain}{sitemap_url}"
                                elif not sitemap_url.startswith(('http://', 'https://')):
                                    sitemap_url = urljoin(base_domain, sitemap_url)
                                
                                if sitemap_url not in sitemaps:
                                    # Verify the sitemap actually exists
                                    if await self._check_file_with_fallback(session, sitemap_url):
                                        sitemaps.append(sitemap_url)
        except Exception:
            pass
        
        # Method 3: Check HTML for sitemap references
        try:
            async with session.get(base_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    if 'text/html' in content_type:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Check for <link rel="sitemap">
                        for link in soup.find_all('link', rel=lambda x: x and 'sitemap' in x.lower()):
                            href = link.get('href', '').strip()
                            if href:
                                absolute_url = urljoin(base_domain, href)
                                if absolute_url not in sitemaps:
                                    # Verify the sitemap actually exists
                                    if await self._check_file_with_fallback(session, absolute_url):
                                        sitemaps.append(absolute_url)
        except Exception:
            pass
        
        return sitemaps