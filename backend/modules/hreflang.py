# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import re
from typing import List, Dict
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from core.soup import soup_for
from database import Database


# BCP-47 primary language subtags that are 2 letters. An incomplete list here
# produced false "invalid code" issues for valid languages such as Catalan,
# Galician, Basque, Norwegian Bokmal or Icelandic.
_ISO_639_1 = frozenset("""
aa ab ae af ak am an ar as av ay az ba be bg bh bi bm bn bo br bs ca ce ch co
cr cs cu cv cy da de dv dz ee el en eo es et eu fa ff fi fj fo fr fy ga gd gl
gn gu gv ha he hi ho hr ht hu hy hz ia id ie ig ii ik io is it iu ja jv ka kg
ki kj kk kl km kn ko kr ks ku kv kw ky la lb lg li ln lo lt lu lv mg mh mi mk
ml mn mr ms mt my na nb nd ne ng nl nn no nr nv ny oc oj om or os pa pi pl ps
pt qu rm rn ro ru rw sa sc sd se sg si sk sl sm sn so sq sr ss st su sv sw ta
te tg th ti tk tl tn to tr ts tt tw ty ug uk ur uz ve vi vo wa wo xh yi yo za
zh zu
""".split())

# Deprecated ISO 639-1 codes still found in the wild.
_LEGACY_LANGUAGE_CODES = frozenset({'sh', 'mo', 'iw', 'in', 'ji', 'jw'})

# Primary language (2-3 letters) plus optional alphanumeric subtags of 1-8
# characters (script, region, variants and extensions).
_HREFLANG_SYNTAX = re.compile(r'^[a-z]{2,3}(?:-[a-z0-9]{1,8})*$')


def is_valid_hreflang_code(code: str) -> bool:
    """Validate a BCP-47 language tag without rejecting unlisted languages."""
    normalized = (code or '').strip().lower()
    if not normalized:
        return False
    if normalized == 'x-default':
        return True
    # Private-use and grandfathered tags (x-..., i-...).
    if normalized.startswith(('x-', 'i-')):
        return True
    if not _HREFLANG_SYNTAX.match(normalized):
        return False

    primary = normalized.split('-', 1)[0]
    if len(primary) == 2:
        return primary in _ISO_639_1 or primary in _LEGACY_LANGUAGE_CODES
    # Three-letter ISO 639-2/3 codes are valid BCP-47 primary subtags; we
    # accept them instead of maintaining another incomplete whitelist.
    return True


class HreflangModule:
    """Module to validate hreflang tags for international SEO"""
    
    def __init__(self, db: Database):
        """
        Initialize the Hreflang module.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def analyze(self, scan_id: int, pages: List[Dict]) -> List[Dict]:
        """
        Analyze website for hreflang issues.
        
        Args:
            scan_id: Scan ID
            pages: List of pages from crawler
        
        Returns:
            List of hreflang issues found
        """
        issues = []
        
        for page in pages:
            if not page.get('html'):
                continue
                
            url = page['url']
            soup = soup_for(page)
            
            hreflang_links = soup.find_all('link', attrs={'rel': 'alternate', 'hreflang': True})
            
            if not hreflang_links:
                continue
            
            hreflang_data = []
            for link in hreflang_links:
                hreflang_value = link.get('hreflang', '').strip()
                href_value = link.get('href', '').strip()
                
                if hreflang_value and href_value:
                    hreflang_data.append({
                        'hreflang': hreflang_value,
                        'href': href_value
                    })
            
            issues.extend(self._check_self_referencing(url, hreflang_data))
            issues.extend(self._check_x_default(url, hreflang_data))
            issues.extend(self._check_duplicate_codes(url, hreflang_data))
            issues.extend(self._check_invalid_codes(url, hreflang_data))
            issues.extend(self._check_return_links(url, hreflang_data, pages))
            issues.extend(self._check_missing_canonical(url, soup))
        
        for issue in issues:
            self.db.add_issue(
                scan_id=scan_id,
                issue_type=issue['issue_type'],
                url=issue['url'],
                source_page=issue['source_page'],
                description=issue['description'],
                severity=issue['severity']
            )
        
        return issues
    
    def _check_self_referencing(self, url: str, hreflang_data: List[Dict]) -> List[Dict]:
        """
        Check if the page references itself with hreflang.
        
        Args:
            url: Current page URL
            hreflang_data: List of hreflang tags
        
        Returns:
            List of issues
        """
        issues = []
        
        normalized_url = url.rstrip('/')
        
        for data in hreflang_data:
            href = data['href'].rstrip('/')
            if href == normalized_url:
                return issues
        
        issues.append({
            'issue_type': 'hreflang_missing_self_reference',
            'url': url,
            'source_page': url,
            'description': 'Page does not reference itself with hreflang tag',
            'severity': 'high'
        })
        
        return issues
    
    def _check_x_default(self, url: str, hreflang_data: List[Dict]) -> List[Dict]:
        """
        Check if x-default is present.
        
        Args:
            url: Current page URL
            hreflang_data: List of hreflang tags
        
        Returns:
            List of issues
        """
        issues = []
        
        has_x_default = any(data['hreflang'] == 'x-default' for data in hreflang_data)
        
        if not has_x_default and len(hreflang_data) > 0:
            issues.append({
                'issue_type': 'hreflang_missing_x_default',
                'url': url,
                'source_page': url,
                'description': 'Missing x-default hreflang tag for non-language-specific version',
                'severity': 'medium'
            })
        
        return issues
    
    def _check_duplicate_codes(self, url: str, hreflang_data: List[Dict]) -> List[Dict]:
        """
        Check for duplicate language codes.
        
        Args:
            url: Current page URL
            hreflang_data: List of hreflang tags
        
        Returns:
            List of issues
        """
        issues = []
        
        seen_codes = {}
        for data in hreflang_data:
            code = data['hreflang']
            if code in seen_codes:
                issues.append({
                    'issue_type': 'hreflang_duplicate_code',
                    'url': url,
                    'source_page': url,
                    'description': f'Duplicate hreflang code "{code}" found. First: {seen_codes[code]}, Second: {data["href"]}',
                    'severity': 'high'
                })
            else:
                seen_codes[code] = data['href']
        
        return issues
    
    def _check_invalid_codes(self, url: str, hreflang_data: List[Dict]) -> List[Dict]:
        """
        Check for invalid language codes.
        
        Args:
            url: Current page URL
            hreflang_data: List of hreflang tags
        
        Returns:
            List of issues
        """
        issues = []
        
        for data in hreflang_data:
            code = data['hreflang']
            
            if not is_valid_hreflang_code(code):
                issues.append({
                    'issue_type': 'hreflang_invalid_code',
                    'url': url,
                    'source_page': url,
                    'description': f'Invalid hreflang code "{code}" found',
                    'severity': 'high'
                })
        
        return issues
    
    def _check_return_links(self, url: str, hreflang_data: List[Dict], pages: List[Dict]) -> List[Dict]:
        """
        Check if hreflang links are bidirectional (return links).
        
        Args:
            url: Current page URL
            hreflang_data: List of hreflang tags
            pages: List of all pages
        
        Returns:
            List of issues
        """
        issues = []
        
        url_to_hreflang = {}
        for page in pages:
            if not page.get('html'):
                continue
            
            soup = soup_for(page)
            hreflang_links = soup.find_all('link', attrs={'rel': 'alternate', 'hreflang': True})
            
            page_hreflangs = {}
            for link in hreflang_links:
                hreflang_value = link.get('hreflang', '').strip()
                href_value = link.get('href', '').strip()
                if hreflang_value and href_value:
                    page_hreflangs[hreflang_value] = href_value
            
            url_to_hreflang[page['url'].rstrip('/')] = page_hreflangs
        
        for data in hreflang_data:
            target_url = data['href'].rstrip('/')
            target_code = data['hreflang']
            
            if target_url not in url_to_hreflang:
                continue
            
            current_code = None
            for h_data in hreflang_data:
                if h_data['href'].rstrip('/') == url.rstrip('/'):
                    current_code = h_data['hreflang']
                    break
            
            if not current_code:
                continue
            
            target_hreflangs = url_to_hreflang[target_url]
            if current_code not in target_hreflangs:
                issues.append({
                    'issue_type': 'hreflang_missing_return_link',
                    'url': url,
                    'source_page': url,
                    'description': f'Missing return link: {target_url} does not reference back to {url} with hreflang="{current_code}"',
                    'severity': 'high'
                })
        
        return issues
    
    def _check_missing_canonical(self, url: str, soup: BeautifulSoup) -> List[Dict]:
        """
        Check if canonical tag is present when hreflang is used.
        
        Args:
            url: Current page URL
            soup: BeautifulSoup object
        
        Returns:
            List of issues
        """
        issues = []
        
        has_hreflang = soup.find('link', attrs={'rel': 'alternate', 'hreflang': True})
        
        if has_hreflang:
            canonical = soup.find('link', attrs={'rel': 'canonical'})
            
            if not canonical:
                issues.append({
                    'issue_type': 'hreflang_missing_canonical',
                    'url': url,
                    'source_page': url,
                    'description': 'Page has hreflang tags but missing canonical tag',
                    'severity': 'high'
                })
        
        return issues