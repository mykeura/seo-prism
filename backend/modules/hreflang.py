# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

from typing import List, Dict
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from core.soup import soup_for
from database import Database


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
        
        valid_codes = {
            'x-default', 'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko',
            'ar', 'hi', 'tr', 'pl', 'nl', 'sv', 'da', 'no', 'fi', 'el', 'cs', 'ro',
            'hu', 'bg', 'sk', 'sl', 'hr', 'sr', 'uk', 'be', 'et', 'lv', 'lt', 'th',
            'vi', 'id', 'ms', 'fil', 'he', 'fa', 'ur', 'bn', 'ta', 'te', 'ml', 'kn',
            'gu', 'mr', 'ne', 'si', 'my', 'km', 'lo', 'ka', 'am', 'sw', 'zu', 'af'
        }
        
        for data in hreflang_data:
            code = data['hreflang']
            
            base_code = code.split('-')[0] if '-' in code else code
            
            if code != 'x-default' and base_code not in valid_codes:
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