# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import asyncio
import aiohttp
from typing import List, Dict, Set, Optional
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from version import __version__
from .url_utils import parse_target_url, is_local, resolve_relative_url, normalize_url

_USER_AGENT = f'Mozilla/5.0 (compatible; SEO-Prism/{__version__}; +https://seo-prism.local)'


# Connection limits. aiohttp defaults to 100 total and unlimited per host.
# 25 covers the crawler's batches of 20 pages and 30 resources without
# artificial queuing; 8 per host stays polite with real servers and avoids
# 429/ban bursts; the DNS cache is reused for 5 minutes.
_MAX_CONNECTIONS = 25
_MAX_CONNECTIONS_PER_HOST = 8
_DNS_CACHE_TTL_SECONDS = 300


class Crawler:
    """Async web crawler for SEO analysis."""
    
    def __init__(self, base_url: str, ignore_robots: bool = False):
        """
        Initialize the crawler.
        
        Args:
            base_url: The starting URL to crawl
            ignore_robots: If True, ignore robots.txt (default for local URLs)
        """
        self.base_url = base_url
        self.ignore_robots = ignore_robots
        
        try:
            self.domain, self.port, self.scheme = parse_target_url(base_url)
        except ValueError as e:
            raise ValueError(f"Invalid base URL: {e}")
        
        self.visited_urls: Set[str] = set()
        self.queued_urls: Set[str] = set()
        self.results: List[Dict] = []
        
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(
            limit=_MAX_CONNECTIONS,
            limit_per_host=_MAX_CONNECTIONS_PER_HOST,
            ttl_dns_cache=_DNS_CACHE_TTL_SECONDS,
        )
        self.session = aiohttp.ClientSession(connector=connector)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _is_same_domain(self, url: str) -> bool:
        """
        Check if URL belongs to the same domain as base URL.
        
        Args:
            url: URL to check
        
        Returns:
            True if same domain, False otherwise
        """
        try:
            parsed = urlparse(url)
            if not parsed.hostname:
                return False
            
            target_domain, target_port, _ = parse_target_url(url)
            return target_domain == self.domain
        except Exception:
            return False
    
    async def _fetch_resource(self, url: str) -> Optional[Dict]:
        """
        Fetch a single resource (image, script, stylesheet) and verify its status.
        
        Args:
            url: URL to fetch
        
        Returns:
            Dictionary with resource info or None if failed
        """
        if not self.session:
            return None
        
        normalized_url = normalize_url(url)
        
        if normalized_url in self.visited_urls:
            return None
        
        self.visited_urls.add(normalized_url)
        
        try:
            headers = {'User-Agent': _USER_AGENT}
            
            # Use HEAD request for resources (faster, doesn't download content)
            async with self.session.head(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                status = response.status
                
                return {
                    'url': normalized_url,
                    'status': status,
                    'links': [],
                    'resources': [],
                    'html': None,
                    'is_resource': True
                }
        
        except asyncio.TimeoutError:
            return {
                'url': normalized_url,
                'status': 408,  # Request Timeout
                'links': [],
                'resources': [],
                'html': None,
                'is_resource': True
            }
        except Exception as e:
            return {
                'url': normalized_url,
                'status': 0,  # Connection error
                'links': [],
                'resources': [],
                'html': None,
                'error': str(e),
                'is_resource': True
            }
    
    async def _fetch_page(self, url: str) -> Optional[Dict]:
        """
        Fetch a single page and extract links.
        
        Args:
            url: URL to fetch
        
        Returns:
            Dictionary with page info or None if failed
        """
        if not self.session:
            return None
        
        normalized_url = normalize_url(url)
        
        if normalized_url in self.visited_urls:
            return None
        
        self.visited_urls.add(normalized_url)
        
        try:
            headers = {'User-Agent': _USER_AGENT}
            
            async with self.session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                status = response.status
                
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type:
                    return {
                        'url': normalized_url,
                        'status': status,
                        'links': [],
                        'resources': [],
                        'html': None
                    }
                
                html = await response.text()
                
                soup = BeautifulSoup(html, 'html.parser')
                internal_links, all_resources = self._extract_links(soup, url)
                
                return {
                    'url': normalized_url,
                    'status': status,
                    'links': internal_links,
                    'resources': all_resources,
                    'html': html
                }
        
        except asyncio.TimeoutError:
            return {
                'url': normalized_url,
                'status': 408,  # Request Timeout
                'links': [],
                'resources': [],
                'html': None
            }
        except Exception as e:
            return {
                'url': normalized_url,
                'status': 0,  # Connection error
                'links': [],
                'resources': [],
                'html': None,
                'error': str(e)
            }
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> tuple[List[str], List[Dict]]:
        """
        Extract all links and resources from a BeautifulSoup object.
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links
        
        Returns:
            Tuple of (internal_links, all_resources)
            internal_links: Links to same domain pages for crawling
            all_resources: All resources found (a, img, link, script) with metadata
        """
        internal_links = []
        all_resources = []
        
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            
            if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                continue
            
            absolute_url = resolve_relative_url(base_url, href)
            
            all_resources.append({
                'url': absolute_url,
                'type': 'anchor',
                'source': base_url
            })
            
            if self._is_same_domain(absolute_url):
                internal_links.append(normalize_url(absolute_url))
        
        for img in soup.find_all('img', src=True):
            src = img['src'].strip()
            if src:
                absolute_url = resolve_relative_url(base_url, src)
                alt = img.get('alt', '').strip()
                all_resources.append({
                    'url': absolute_url,
                    'type': 'image',
                    'source': base_url,
                    'alt': alt
                })
        
        for link_tag in soup.find_all('link', href=True):
            href = link_tag['href'].strip()
            if href:
                absolute_url = resolve_relative_url(base_url, href)
                all_resources.append({
                    'url': absolute_url,
                    'type': link_tag.get('rel', [''])[0] if link_tag.get('rel') else 'link',
                    'source': base_url
                })
        
        for script in soup.find_all('script', src=True):
            src = script['src'].strip()
            if src:
                absolute_url = resolve_relative_url(base_url, src)
                all_resources.append({
                    'url': absolute_url,
                    'type': 'script',
                    'source': base_url
                })
        
        return list(set(internal_links)), all_resources
    
    async def crawl(self, max_pages: int = 1000) -> List[Dict]:
        """
        Crawl the website starting from base URL.
        
        Args:
            max_pages: Maximum number of pages to crawl
        
        Returns:
            List of page results
        """
        if not self.session:
            raise RuntimeError("Crawler must be used as async context manager")
        
        results = []
        urls_to_visit = [self.base_url]
        self.queued_urls.add(normalize_url(self.base_url))
        resources_to_verify: Set[str] = set()
        external_links_to_verify: Set[str] = set()
        
        while urls_to_visit and len(results) < max_pages:
            current_batch = urls_to_visit[:20]
            urls_to_visit = urls_to_visit[20:]
            
            tasks = [self._fetch_page(url) for url in current_batch]
            page_results = await asyncio.gather(*tasks)
            
            for result in page_results:
                if result:
                    results.append(result)
                    
                    if result['links']:
                        for link in result['links']:
                            if link not in self.visited_urls and link not in self.queued_urls:
                                self.queued_urls.add(link)
                                urls_to_visit.append(link)
                    
                    if result.get('resources'):
                        for resource in result['resources']:
                            resource_url = resource['url']
                            
                            if self._is_same_domain(resource_url) and resource_url not in self.visited_urls:
                                resources_to_verify.add(resource_url)
                            # External resources — anchors as well as images,
                            # scripts and stylesheets — are verified too.
                            elif not self._is_same_domain(resource_url) and resource_url not in self.visited_urls:
                                external_links_to_verify.add(resource_url)
        
        if resources_to_verify:
            resource_list = list(resources_to_verify)
            batch_size = 30
            
            for i in range(0, len(resource_list), batch_size):
                current_batch = resource_list[i:i + batch_size]
                tasks = [self._fetch_resource(url) for url in current_batch]
                resource_results = await asyncio.gather(*tasks)
                
                for resource_result in resource_results:
                    if resource_result:
                        results.append(resource_result)
        
        if external_links_to_verify:
            external_links_list = list(external_links_to_verify)
            batch_size = 30
            
            for i in range(0, len(external_links_list), batch_size):
                current_batch = external_links_list[i:i + batch_size]
                tasks = [self._fetch_resource(url) for url in current_batch]
                external_link_results = await asyncio.gather(*tasks)
                
                for external_link_result in external_link_results:
                    if external_link_result:
                        results.append(external_link_result)
        
        self.results = results
        return results