# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import asyncio
import aiohttp
from typing import List, Dict, Set, Optional, Tuple
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from version import __version__
from .net_guard import NetworkGuard, build_connector
from .robots import HostKey, RobotsCache, host_key
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
    
    def __init__(self, base_url: str, ignore_robots: bool = False,
                 guard: Optional[NetworkGuard] = None):
        """
        Initialize the crawler.
        
        Args:
            base_url: The starting URL to crawl
            ignore_robots: If True, ignore robots.txt (default for local URLs)
            guard: Optional SSRF guard applied to every HTTP connection
        """
        self.base_url = base_url
        self.ignore_robots = ignore_robots
        self.guard = guard or NetworkGuard(False)
        
        try:
            self.domain, self.port, self.scheme = parse_target_url(base_url)
        except ValueError as e:
            raise ValueError(f"Invalid base URL: {e}")
        
        self.visited_urls: Set[str] = set()
        self.queued_urls: Set[str] = set()
        self.results: List[Dict] = []
        self._base_normalized = normalize_url(base_url)
        # URLs robots.txt disallowed for this crawler; they are never fetched.
        self.robots_skipped_urls: Set[str] = set()

        self._robots: Optional[RobotsCache] = None
        self._robots_host: Optional[HostKey] = None
        self._host_next_allowed: Dict[HostKey, float] = {}
        self._pacing_locks: Dict[HostKey, asyncio.Lock] = {}

        self.session: Optional[aiohttp.ClientSession] = None

    @property
    def robots_skipped_count(self) -> int:
        """How many URLs robots.txt disallowed during the last crawl()."""
        return len(self.robots_skipped_urls)
    
    async def __aenter__(self):
        """Async context manager entry."""
        connector = build_connector(
            self.guard,
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
    
    @staticmethod
    def _without_www(domain: str) -> str:
        return domain[4:] if domain.startswith('www.') else domain

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
            # apex <-> www is the same site for crawl purposes; http/https
            # and default-port differences are already normalized away by
            # parse_target_url.
            return self._without_www(target_domain) == self._without_www(self.domain)
        except Exception:
            return False
    
    async def _filter_allowed(self, urls: List[str]) -> List[str]:
        """Drop URLs robots.txt disallows for this crawler, counting each skip.

        Only the crawled host's robots.txt is consulted: URLs pointing
        elsewhere pass through untouched so no third-party robots.txt is
        ever fetched.
        """
        if self._robots is None or self._robots_host is None:
            return urls
        allowed = []
        for url in urls:
            if host_key(url) != self._robots_host:
                allowed.append(url)
                continue
            rules = await self._robots.rules_for(url)
            if rules.can_fetch(url):
                allowed.append(url)
            else:
                self.robots_skipped_urls.add(normalize_url(url))
        return allowed

    async def _pace(self, url: str) -> None:
        """Wait so consecutive requests to one host keep its Crawl-delay.

        No-op unless the host's robots.txt defines a pause; hosts without
        one keep the current unpaced behaviour.
        """
        if self._robots is None or self._robots_host is None:
            return
        if host_key(url) != self._robots_host:
            return
        delay = (await self._robots.rules_for(url)).delay_for(url)
        if not delay:
            return
        lock = self._pacing_locks.setdefault(self._robots_host, asyncio.Lock())
        async with lock:
            loop = asyncio.get_running_loop()
            wait = self._host_next_allowed.get(self._robots_host, 0.0) - loop.time()
            if wait > 0:
                await asyncio.sleep(wait)
            self._host_next_allowed[self._robots_host] = loop.time() + delay

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

        await self._pace(url)

        try:
            headers = {'User-Agent': _USER_AGENT}

            # Prefer HEAD for resources (faster, doesn't download content)
            async with self.session.head(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                status = response.status
            
            # Some servers don't implement HEAD and answer 405/501 even though the
            # resource is fine over GET; retry so healthy resources aren't reported
            # as broken. Only the GET status is used, its body is discarded.
            if status in (405, 501):
                async with self.session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as get_response:
                    status = get_response.status
            
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
    
    @staticmethod
    def _redirect_only_result(requested_url: str, final_url: str,
                              redirect_status: Optional[int],
                              final_status: int,
                              redirect_chain: List[str]) -> Dict:
        """Result for a URL that redirects somewhere we will not analyse."""
        return {
            'url': requested_url,
            'status': redirect_status if redirect_status is not None else final_status,
            'links': [],
            'resources': [],
            'html': None,
            'is_redirect': True,
            'requested_url': requested_url,
            'final_url': final_url,
            'redirect_status': redirect_status,
            'final_status': final_status,
            'redirect_chain': redirect_chain,
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

        await self._pace(url)

        try:
            headers = {'User-Agent': _USER_AGENT}

            async with self.session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                status = response.status
                final_url_raw = str(getattr(response, 'url', None) or url)
                final_url = normalize_url(final_url_raw)
                history = tuple(getattr(response, 'history', ()) or ())
                redirect_status = (
                    getattr(history[0], 'status', None) if history else None
                )
                redirected = bool(history) and final_url != normalized_url
                redirect_chain = []
                if history:
                    redirect_chain = [
                        normalize_url(str(hop_url))
                        for hop_url in (getattr(hop, 'url', None) for hop in history)
                        if hop_url
                    ]
                    redirect_chain.append(final_url)

                is_scan_root = normalized_url == self._base_normalized

                # Internal links that redirect to another host point outside
                # the scanned site: record the hop, but never analyse the
                # external document as if it belonged to the site.
                if redirected and not is_scan_root and not self._is_same_domain(final_url):
                    self.visited_urls.add(final_url)
                    return self._redirect_only_result(
                        normalized_url, final_url, redirect_status, status,
                        redirect_chain)

                if redirected:
                    if final_url in self.visited_urls:
                        return self._redirect_only_result(
                            normalized_url, final_url, redirect_status, status,
                            redirect_chain)
                    self.visited_urls.add(final_url)

                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type:
                    result = {
                        'url': final_url,
                        'status': status,
                        'links': [],
                        'resources': [],
                        'html': None
                    }
                    if redirected:
                        result.update({
                            'requested_url': normalized_url,
                            'final_url': final_url,
                            'redirect_status': redirect_status,
                            'final_status': status,
                            'redirect_chain': redirect_chain,
                        })
                    return result
                
                html = await response.text()

                # The scan root may legitimately redirect to another origin
                # (http -> https, apex -> www, a moved site): adopt the final
                # origin so its links are still crawled as internal.
                if is_scan_root and redirected:
                    try:
                        self.domain, self.port, self.scheme = parse_target_url(final_url)
                    except ValueError:
                        pass
                    if self._robots is not None:
                        new_host = host_key(final_url)
                        if new_host != self._robots_host:
                            self._robots_host = new_host
                            await self._robots.rules_for(final_url)
                
                soup = BeautifulSoup(html, 'html.parser')
                # Relative links resolve against the raw final URL: the
                # normalized form drops the trailing slash and would turn
                # /target/relative.html into /relative.html.
                internal_links, all_resources = self._extract_links(
                    soup, final_url_raw)
                
                result = {
                    'url': final_url,
                    'status': status,
                    'links': internal_links,
                    'resources': all_resources,
                    'html': html
                }
                if redirected:
                    result.update({
                        'requested_url': normalized_url,
                        'final_url': final_url,
                        'redirect_status': redirect_status,
                        'final_status': status,
                        'redirect_chain': redirect_chain,
                    })
                return result
        
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
            List of page results. When robots.txt is respected
            (ignore_robots=False) URLs it disallows for this crawler's
            user agent are never fetched; their count is exposed as
            robots_skipped_count / robots_skipped_urls.
        """
        if not self.session:
            raise RuntimeError("Crawler must be used as async context manager")

        max_pages = max(1, max_pages)
        results = []
        urls_to_visit = [self.base_url]
        self.queued_urls.add(normalize_url(self.base_url))
        resources_to_verify: Set[str] = set()
        external_links_to_verify: Set[str] = set()

        if not self.ignore_robots:
            # Fetched once per host and cached; a missing or unreachable
            # robots.txt yields allow-all rules, so the scan proceeds.
            self._robots = RobotsCache(self.session, _USER_AGENT)
            self._robots_host = host_key(self.base_url)
            await self._robots.rules_for(self.base_url)

        while urls_to_visit and len(results) < max_pages:
            # Never request more pages than the remaining budget: the old
            # fixed 20-item batch overshot max_pages whenever a page exposed
            # twenty or more links (e.g. max_pages=5 crawled 21 pages).
            batch_size = min(20, max_pages - len(results))
            current_batch = urls_to_visit[:batch_size]
            urls_to_visit = urls_to_visit[batch_size:]

            current_batch = await self._filter_allowed(current_batch)

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
        
        # Same-host resources and anchors are HEAD-verified too; a robots.txt
        # disallow means no request at all, so they are filtered as well.
        resources_to_verify = await self._filter_allowed(list(resources_to_verify))

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