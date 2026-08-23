"""
Canonical Tags Analysis Module

Analyzes canonical tags for SEO issues including:
- Missing canonical tags
- Canonical chains (circular or excessive)
- Canonicals to non-existent pages (404)
- Canonicals to redirected pages (301/302)
- Canonical URL variations (http/https, www/non-www)
- Self-canonicals (normal, just informational)
"""

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Set


class CanonicalTagsModule:
    """Analyzes canonical tags for SEO issues."""
    
    def __init__(self, db):
        """
        Initialize the canonical tags module.

        Args:
            db: Database instance
        """
        self.db = db

    def _report(self, issues: List[Dict], scan_id: int, issue: Dict) -> None:
        """
        Register an issue: append it to the result list and persist it to
        the database, so canonical findings are counted AND visible in every
        output (web, CLI, JSON, reports). Tolerates db=None for unit tests.

        Args:
            issues: Accumulated issue list
            scan_id: Scan ID
            issue: Issue dictionary
        """
        issues.append(issue)
        if self.db:
            self.db.add_issue(
                scan_id=scan_id,
                issue_type=issue['issue_type'],
                url=issue['url'],
                source_page=issue['source_page'],
                description=issue['description'],
                severity=issue['severity']
            )
    
    def analyze(self, scan_id: int, crawled_pages: List[Dict]) -> List[Dict]:
        """
        Analyze canonical tags across all pages.
        
        Args:
            scan_id: Scan ID
            crawled_pages: List of crawled pages with HTML content
        
        Returns:
            List of canonical issues found
        """
        issues = []
        
        # Build canonical mapping and page status map
        canonical_map = {}
        page_status_map = {}
        
        for page in crawled_pages:
            url = page.get('url', '')
            status = page.get('status', 0)
            html = page.get('html')
            
            # Always add to page_status_map (even if html is None)
            page_status_map[url] = status
            
            # Only extract canonical if page has HTML
            if html:
                canonical_url = self._extract_canonical(html, url)
                if canonical_url:
                    canonical_map[url] = canonical_url
        
        # Track visited canonicals for chain detection
        visited_canonicals: Set[str] = set()
        
        # Analyze each page
        for page in crawled_pages:
            if page.get('html'):
                soup = BeautifulSoup(page['html'], 'html.parser')
                canonical_tag = soup.find('link', rel='canonical')
                
                page_url = page['url']
                
                # 1. Missing canonical on indexable pages
                if not canonical_tag:
                    if self._should_have_canonical(page):
                        self._report(issues, scan_id, {
                            'issue_type': 'missing_canonical',
                            'url': page_url,
                            'source_page': page_url,
                            'description': 'Page is missing canonical tag',
                            'severity': 'low'
                        })
                    continue

                canonical_href = canonical_tag.get('href', '').strip()
                if not canonical_href:
                    self._report(issues, scan_id, {
                        'issue_type': 'empty_canonical',
                        'url': page_url,
                        'source_page': page_url,
                        'description': 'Canonical tag has empty href attribute',
                        'severity': 'medium'
                    })
                    continue
                
                # Resolve relative URLs
                canonical_url = urljoin(page_url, canonical_href)
                
                # Normalize for all checks
                normalized_canonical = self._normalize_url(canonical_url)
                normalized_page_url = self._normalize_url(page_url)
                
                # 2. Self-canonical (points to self) - normal, just informational
                if normalized_canonical == normalized_page_url:
                    # Self-canonical is correct, no issue
                    continue
                
                # 3. Canonical chains - check using normalized URLs
                canonical_map_normalized = {self._normalize_url(k): self._normalize_url(v) for k, v in canonical_map.items()}
                
                if normalized_canonical in canonical_map_normalized:
                    # Get the normalized target canonical
                    target_canonical_normalized = canonical_map_normalized[normalized_canonical]
                    
                    # Check for circular chain (points back to original page)
                    if target_canonical_normalized == normalized_page_url:
                        self._report(issues, scan_id, {
                            'issue_type': 'canonical_chain',
                            'url': page_url,
                            'source_page': page_url,
                            'description': f'Circular canonical chain detected: {page_url} → {canonical_url} → {page_url}',
                            'severity': 'high'
                        })
                    # Check for excessive chain
                    elif len(self._trace_canonical_chain(canonical_map, page_url, visited=set())) > 2:
                        self._report(issues, scan_id, {
                            'issue_type': 'canonical_chain',
                            'url': page_url,
                            'source_page': page_url,
                            'description': f'Excessive canonical chain detected: {self._format_chain(canonical_map, page_url)}',
                            'severity': 'high'
                        })
                
                # 4. Canonical to non-existent page (404)
                target_status = page_status_map.get(normalized_canonical)
                
                if target_status is not None and target_status >= 400:
                    self._report(issues, scan_id, {
                        'issue_type': 'canonical_to_404',
                        'url': page_url,
                        'source_page': page_url,
                        'description': f'Canonical points to non-existent page ({target_status}): {canonical_url}',
                        'severity': 'high'
                    })

                # 5. Canonical to redirected page (301/302)
                elif target_status is not None and target_status in [301, 302]:
                    self._report(issues, scan_id, {
                        'issue_type': 'canonical_to_redirect',
                        'url': page_url,
                        'source_page': page_url,
                        'description': f'Canonical points to redirected page ({target_status}): {canonical_url}',
                        'severity': 'medium'
                    })

                # 6. Canonical URL variations (only for production, not localhost)
                elif not self._is_development_environment(page_url):
                    if self._has_url_variation(page_url, canonical_url):
                        variation_type = self._get_variation_type(page_url, canonical_url)
                        self._report(issues, scan_id, {
                            'issue_type': 'canonical_url_variation',
                            'url': page_url,
                            'source_page': page_url,
                            'description': f'Canonical points to URL with {variation_type}: {canonical_url}',
                            'severity': 'low'
                        })
        
        return issues
    
    def _extract_canonical(self, html: str, page_url: str) -> str:
        """
        Extract canonical URL from HTML.
        
        Args:
            html: HTML content
            page_url: Page URL for resolving relative URLs
        
        Returns:
            Canonical URL or None
        """
        soup = BeautifulSoup(html, 'html.parser')
        canonical_tag = soup.find('link', rel='canonical')
        if canonical_tag and canonical_tag.get('href'):
            href = canonical_tag.get('href', '').strip()
            return urljoin(page_url, href)
        return None
    
    def _should_have_canonical(self, page: Dict) -> bool:
        """
        Determine if page should have canonical tag.
        
        Args:
            page: Page dictionary
        
        Returns:
            True if page should have canonical
        """
        # For now, assume all HTML pages should have canonical
        # Could be refined to check for noindex meta tag
        return True
    
    def _is_development_environment(self, url: str) -> bool:
        """
        Check if URL is in development environment.
        
        Args:
            url: URL to check
        
        Returns:
            True if development environment
        """
        parsed = urlparse(url)
        hostname = parsed.hostname or ''
        
        return (
            'localhost' in hostname or
            '127.0.0.1' in hostname or
            hostname.startswith('192.168.') or
            hostname.startswith('10.') or
            hostname.startswith('172.')
        )
    
    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL for comparison.
        
        Args:
            url: URL to normalize
        
        Returns:
            Normalized URL
        """
        parsed = urlparse(url)
        
        # Remove trailing slash
        path = parsed.path.rstrip('/')
        
        # Reconstruct URL without fragment
        normalized = f"{parsed.scheme}://{parsed.netloc}{path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        
        return normalized.lower()
    
    def _has_url_variation(self, url1: str, url2: str) -> bool:
        """
        Check if URLs are variations of each other.
        
        Args:
            url1: First URL
            url2: Second URL
        
        Returns:
            True if URLs are variations
        """
        parsed1 = urlparse(url1)
        parsed2 = urlparse(url2)
        
        # Check path and query match
        if parsed1.path != parsed2.path or parsed1.query != parsed2.query:
            return False
        
        # Check for www variation
        hostname1 = parsed1.hostname or ''
        hostname2 = parsed2.hostname or ''
        
        if hostname1.replace('www.', '') == hostname2.replace('www.', ''):
            return True
        
        # Check for http/https variation
        if parsed1.scheme != parsed2.scheme:
            return True
        
        return False
    
    def _get_variation_type(self, url1: str, url2: str) -> str:
        """
        Get the type of variation between URLs.
        
        Args:
            url1: First URL
            url2: Second URL
        
        Returns:
            Type of variation
        """
        parsed1 = urlparse(url1)
        parsed2 = urlparse(url2)
        
        hostname1 = parsed1.hostname or ''
        hostname2 = parsed2.hostname or ''
        
        # Check for www variation
        if 'www.' in hostname1 or 'www.' in hostname2:
            if hostname1.replace('www.', '') == hostname2.replace('www.', ''):
                return 'www/non-www variation'
        
        # Check for http/https variation
        if parsed1.scheme != parsed2.scheme:
            return 'http/https variation'
        
        return 'URL variation'
    
    def _trace_canonical_chain(self, canonical_map: Dict, start_url: str, visited: Set[str], depth: int = 0) -> List[str]:
        """
        Trace canonical chain to detect circular or excessive chains.
        
        Args:
            canonical_map: Mapping of URLs to their canonicals
            start_url: Starting URL
            visited: Set of visited URLs
            depth: Current depth (max 5)
        
        Returns:
            List of URLs in the chain
        """
        if depth > 5 or start_url in visited:
            return []
        
        visited.add(start_url)
        
        if start_url not in canonical_map:
            return [start_url]
        
        target = canonical_map[start_url]
        if target == start_url:
            return [start_url]
        
        chain = [start_url]
        chain.extend(self._trace_canonical_chain(canonical_map, target, visited.copy(), depth + 1))
        
        return chain
    
    def _format_chain(self, canonical_map: Dict, start_url: str) -> str:
        """
        Format canonical chain for display.
        
        Args:
            canonical_map: Mapping of URLs to their canonicals
            start_url: Starting URL
        
        Returns:
            Formatted chain string
        """
        chain = self._trace_canonical_chain(canonical_map, start_url, set())
        return ' → '.join(chain)