# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""Regression: crawl batches must never exceed max_pages.

Historic bug: each iteration fetched a fixed batch of 20 URLs after checking
max_pages only once, so a page linking 20+ URLs made the crawler overshoot
the requested cap (max_pages=5 crawled 21 pages).
"""
import asyncio

import pytest

from core.crawler import Crawler
from core.url_utils import normalize_url


class _FakeCrawler(Crawler):
    """Every fetched page exposes 30 new links, so batches stay full."""

    def __init__(self):
        super().__init__('http://localhost/', ignore_robots=True)
        self.session = object()
        self.fetched = 0

    async def _pace(self, url):
        pass

    async def _fetch_page(self, url):
        page_url = normalize_url(url)
        if page_url in self.visited_urls:
            return None
        self.visited_urls.add(page_url)
        self.fetched += 1
        links = [f'http://localhost/p{self.fetched}-{i}' for i in range(30)]
        return {
            'url': page_url,
            'status': 200,
            'links': links,
            'resources': [],
            'html': '<html></html>',
        }


@pytest.mark.parametrize('max_pages', [1, 5, 25, 100])
def test_crawl_never_exceeds_max_pages(max_pages):
    crawler = _FakeCrawler()

    pages = asyncio.run(crawler.crawl(max_pages=max_pages))

    assert len(pages) == max_pages


def test_zero_max_pages_is_normalised_to_one():
    crawler = _FakeCrawler()

    pages = asyncio.run(crawler.crawl(max_pages=0))

    assert len(pages) == 1
