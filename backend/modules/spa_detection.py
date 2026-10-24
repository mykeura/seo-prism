# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""Detection of JavaScript-rendered sites (SPAs) from the crawled HTML.

The crawler fetches raw HTML without executing JavaScript, so on a SPA the
analysis sees an empty app shell and reports missing titles, empty H1s and
thin content that do not match what a browser shows. When a significant
fraction of the crawled pages looks JS-rendered, the report carries one
low-severity notice instead of that misleading cascade of issues.
"""

import re
from typing import Dict, List

from bs4 import BeautifulSoup
from database import Database

# ids under which React/Vue/Angular/Next mount their application
_ROOT_CONTAINER_IDS = {'root', 'app', 'main', '__next'}

# Noise inside the mount point that is not page content
_CONTAINER_NOISE = ('script', 'style', 'noscript', 'template', 'svg')

# Framework fingerprints that survive in the raw HTML of a JS-rendered page
_FRAMEWORK_MARKERS = (
    '__next_data__',    # Next.js pages router
    '/_next/static',    # Next.js app router bundles
    '__nuxt__',         # Nuxt payload
    '/_nuxt/',          # Nuxt asset path
    'data-reactroot',   # React
    'data-v-app',       # Vue 3 mount
    '__vue__',          # Vue
    'ng-app',           # AngularJS bootstrap
    'ng-version',       # Angular 2+
)

_FRAMEWORK_SCRIPT_RE = re.compile(
    r'(?:src|href)=["\'][^"\']*\b(?:react-dom|react|vue|angular|nuxt|svelte)[.\w-]*\.js',
    re.IGNORECASE,
)

_NOSCRIPT_WARNING_RE = re.compile(r'javascript', re.IGNORECASE)


class SpaDetectionModule:
    """Module to warn when a site looks JavaScript-rendered (SPA)."""

    # Fraction of analyzed pages that must look JS-rendered to flag the site
    JS_RENDERED_FRACTION = 0.5
    DESCRIPTION = (
        'The site appears to be a JavaScript-rendered application (SPA): the '
        'crawl is based on unrendered HTML, so titles and content may appear '
        'missing even though they are visible in a browser'
    )

    def __init__(self, db: Database):
        """
        Initialize the SPA Detection module.

        Args:
            db: Database instance
        """
        self.db = db

    def analyze(self, scan_id: int, crawled_pages: List[Dict], base_url: str) -> List[Dict]:
        """
        Emit a single informative issue when most analyzed pages look JS-rendered.

        Args:
            scan_id: Scan ID
            crawled_pages: List of crawled page results
            base_url: Base URL of the scanned site

        Returns:
            List with one 'spa_detected' issue, or empty when the site does
            not look JS-rendered
        """
        issues = []
        pages = [page for page in crawled_pages
                 if page.get('html') and not page.get('is_resource', False)]

        if not pages:
            return issues

        rendered = sum(1 for page in pages if self._looks_js_rendered(page['html']))
        if rendered / len(pages) < self.JS_RENDERED_FRACTION:
            return issues

        issue = {
            'issue_type': 'spa_detected',
            'url': base_url,
            'source_page': base_url,
            'description': self.DESCRIPTION,
            'severity': 'low'
        }
        issues.append(issue)

        self.db.add_issue(
            scan_id=scan_id,
            issue_type='spa_detected',
            url=base_url,
            source_page=base_url,
            description=self.DESCRIPTION,
            severity='low'
        )

        return issues

    def _looks_js_rendered(self, html: str) -> bool:
        """
        Check whether one page's HTML looks like a JS-rendered app shell.

        Args:
            html: Raw HTML of the page

        Returns:
            True when a framework fingerprint, an empty root container or a
            noscript JavaScript warning is present
        """
        lowered = html.lower()
        if any(marker in lowered for marker in _FRAMEWORK_MARKERS):
            return True
        if _FRAMEWORK_SCRIPT_RE.search(html):
            return True

        soup = BeautifulSoup(html, 'html.parser')
        return self._has_empty_root_container(soup) or self._has_noscript_warning(soup)

    def _has_empty_root_container(self, soup: BeautifulSoup) -> bool:
        """
        Check for a typical SPA mount point holding no visible text.

        Args:
            soup: BeautifulSoup tree of the page

        Returns:
            True when a div with a typical root id contains no text other
            than scripts/styles/templates
        """
        container = soup.find(
            'div', id=lambda value: value and value.strip().lower() in _ROOT_CONTAINER_IDS
        )
        if container is None:
            return False

        for noise in container.find_all(list(_CONTAINER_NOISE)):
            noise.decompose()

        return container.get_text(strip=True) == ''

    def _has_noscript_warning(self, soup: BeautifulSoup) -> bool:
        """
        Check for a <noscript> telling the visitor to enable JavaScript.

        Args:
            soup: BeautifulSoup tree of the page

        Returns:
            True when a noscript block mentions JavaScript
        """
        return any(
            _NOSCRIPT_WARNING_RE.search(noscript.get_text())
            for noscript in soup.find_all('noscript')
        )
