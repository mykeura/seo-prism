# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""Tests for the HTTP API request guards (max_pages clamp)."""
import pytest
from fastapi.testclient import TestClient

import api.main as main


class _FakeDB:
    def close(self):
        pass


@pytest.fixture
def client(monkeypatch):
    captured = {}

    async def fake_pipeline(db, url, max_pages, ignore_robots):
        captured['max_pages'] = max_pages
        return {
            'scan_id': 1,
            'html_page_count': 3,
            'issues': [],
            'seo_grade': {'grade': 'B', 'score': 85},
            'resource_analysis': {},
        }

    monkeypatch.setattr(main, 'Database', lambda *a, **k: _FakeDB())
    monkeypatch.setattr(main, 'run_scan_pipeline', fake_pipeline)
    return TestClient(main.app), captured


@pytest.mark.parametrize('sent,expected', [
    (99999, 100),
    (100, 100),
    (1, 1),
    (0, 1),
    (-5, 1),
    (None, 100),
])
def test_scan_clamps_max_pages(client, sent, expected):
    http, captured = client
    resp = http.post('/scan', json={'url': 'http://127.0.0.1:1', 'max_pages': sent})
    assert resp.status_code == 200
    assert captured['max_pages'] == expected


def test_scan_rejects_invalid_url(client):
    http, _ = client
    assert http.post('/scan', json={'url': 'not-a-url'}).status_code == 400
