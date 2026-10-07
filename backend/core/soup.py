# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

from typing import Dict, Optional

from bs4 import BeautifulSoup


def soup_for(page: Dict) -> Optional[BeautifulSoup]:
    """
    Return a BeautifulSoup parse of page['html'], cached on the page dict.

    Analysis modules used to re-parse the same HTML once per module; caching
    the soup under the '_soup' key means each page is parsed at most once
    per scan.

    Args:
        page: Crawled page dict (must have a 'html' key or none)

    Returns:
        BeautifulSoup tree, or None when the page has no HTML
    """
    soup = page.get('_soup')
    if soup is None:
        html = page.get('html')
        if not html:
            return None
        soup = BeautifulSoup(html, 'html.parser')
        page['_soup'] = soup
    return soup
