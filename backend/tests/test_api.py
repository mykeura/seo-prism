# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
Tests for the HTTP API guards: optional max_pages limit, optional API key,
opt-in private-target guard, health endpoint, scan history and error
sanitization.
"""
import re
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

import api.main as main
from core.pipeline import ScanBlockedByRobots, ScanTargetUnreachable
from database import Database
from limits import get_max_pages_limit
from modules.seo_grade import SEOGradeCalculator


class _FakeDB:
    def close(self):
        pass


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for var in ('SEO_PRISM_MAX_PAGES_LIMIT', 'SEO_PRISM_API_KEY',
                'SEO_PRISM_BLOCK_PRIVATE_TARGETS'):
        monkeypatch.delenv(var, raising=False)


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


@pytest.fixture
def db_client(monkeypatch, tmp_path):
    """Client backed by a real on-disk Database, for the /scans history.

    Like in production, every request opens its own connection; the yielded
    handle exists only to seed data from the test's thread.
    """
    db_path = str(tmp_path / 'scans.db')
    monkeypatch.setattr(main, 'Database', lambda *a, **k: Database(db_path))

    db = Database(db_path)
    yield TestClient(main.app), db
    db.close()


def _seed_scan(db, url, pages, issues):
    """Store a scan the way the pipeline would: totals plus issue rows."""
    scan_id = db.create_scan(url)
    for severity, count in issues.items():
        for _ in range(count):
            db.add_issue(scan_id, 'test_issue', url, severity=severity)
    db.update_scan_totals(scan_id, pages, sum(issues.values()))
    return scan_id


# --- max_pages limit -------------------------------------------------------

@pytest.mark.parametrize('sent,expected', [
    (None, 100),
    (1, 1),
    (0, 1),
    (-5, 1),
    (99999, 99999),
])
def test_scan_without_env_limit_has_no_ceiling(client, sent, expected):
    http, captured = client
    resp = http.post('/scan', json={'url': 'http://127.0.0.1:1', 'max_pages': sent})
    assert resp.status_code == 200
    assert captured['max_pages'] == expected


@pytest.mark.parametrize('sent,expected', [
    (99999, 50),
    (100, 50),
    (25, 25),
    (0, 1),
    (None, 50),
])
def test_scan_clamps_only_when_env_limit_is_set(client, monkeypatch, sent, expected):
    monkeypatch.setenv('SEO_PRISM_MAX_PAGES_LIMIT', '50')
    http, captured = client
    resp = http.post('/scan', json={'url': 'http://127.0.0.1:1', 'max_pages': sent})
    assert resp.status_code == 200
    assert captured['max_pages'] == expected


@pytest.mark.parametrize('raw', ['not-a-number', '0', '-3', ''])
def test_scan_ignores_invalid_env_limit(client, monkeypatch, raw):
    monkeypatch.setenv('SEO_PRISM_MAX_PAGES_LIMIT', raw)
    http, captured = client
    resp = http.post('/scan', json={'url': 'http://127.0.0.1:1', 'max_pages': 200})
    assert resp.status_code == 200
    assert captured['max_pages'] == 200


def test_get_max_pages_limit_reads_env(monkeypatch):
    monkeypatch.delenv('SEO_PRISM_MAX_PAGES_LIMIT', raising=False)
    assert get_max_pages_limit() is None
    monkeypatch.setenv('SEO_PRISM_MAX_PAGES_LIMIT', '42')
    assert get_max_pages_limit() == 42
    monkeypatch.setenv('SEO_PRISM_MAX_PAGES_LIMIT', 'nope')
    assert get_max_pages_limit() is None


# --- /health ----------------------------------------------------------------

def test_health_ok(client):
    http, _ = client
    resp = http.get('/health')
    assert resp.status_code == 200
    assert resp.json() == {'status': 'ok', 'version': main.__version__}


def test_health_open_even_with_api_key(client, monkeypatch):
    monkeypatch.setenv('SEO_PRISM_API_KEY', 'sekrit')
    http, _ = client
    resp = http.get('/health')
    assert resp.status_code == 200


# --- API key ----------------------------------------------------------------

def test_endpoints_open_without_api_key_env(client):
    http, _ = client
    assert http.post('/scan', json={'url': 'http://127.0.0.1:1'}).status_code == 200
    assert http.get('/').status_code == 200


def test_api_key_missing_rejected(client, monkeypatch):
    monkeypatch.setenv('SEO_PRISM_API_KEY', 'sekrit')
    http, captured = client
    resp = http.post('/scan', json={'url': 'http://127.0.0.1:1'})
    assert resp.status_code == 401
    assert resp.json() == {'detail': 'Unauthorized'}
    assert 'max_pages' not in captured


def test_api_key_incorrect_rejected(client, monkeypatch):
    monkeypatch.setenv('SEO_PRISM_API_KEY', 'sekrit')
    http, _ = client
    resp = http.post('/scan', json={'url': 'http://127.0.0.1:1'},
                     headers={'X-API-Key': 'wrong-value'})
    assert resp.status_code == 401
    # Missing and incorrect keys must be indistinguishable.
    assert resp.json() == {'detail': 'Unauthorized'}


def test_api_key_required_on_every_endpoint(client, monkeypatch):
    monkeypatch.setenv('SEO_PRISM_API_KEY', 'sekrit')
    http, _ = client
    assert http.get('/').status_code == 401
    assert http.get('/scans').status_code == 401
    assert http.get('/results').status_code == 401
    assert http.get('/results/1').status_code == 401


def test_api_key_correct_accepted(client, monkeypatch):
    monkeypatch.setenv('SEO_PRISM_API_KEY', 'sekrit')
    http, captured = client
    resp = http.post('/scan', json={'url': 'http://127.0.0.1:1'},
                     headers={'X-API-Key': 'sekrit'})
    assert resp.status_code == 200
    assert 'max_pages' in captured


# --- private-target guard -----------------------------------------------------

def test_scan_blocks_private_target_when_guard_enabled(client, monkeypatch):
    monkeypatch.setenv('SEO_PRISM_BLOCK_PRIVATE_TARGETS', '1')
    http, captured = client
    resp = http.post('/scan', json={'url': 'http://127.0.0.1:1'})
    assert resp.status_code == 400
    assert 'non-public' in resp.json()['detail']
    assert 'max_pages' not in captured


def test_scan_allows_private_target_without_guard(client):
    http, captured = client
    resp = http.post('/scan', json={'url': 'http://127.0.0.1:1'})
    assert resp.status_code == 200
    assert 'max_pages' in captured


# --- error hygiene --------------------------------------------------------------

def test_scan_unreachable_returns_502(client, monkeypatch):
    async def unreachable(db, url, max_pages, ignore_robots):
        raise ScanTargetUnreachable(f"Could not reach '{url}'")

    monkeypatch.setattr(main, 'run_scan_pipeline', unreachable)
    http, _ = client

    resp = http.post('/scan', json={'url': 'http://example.com'})

    assert resp.status_code == 502
    assert resp.json() == {'detail': "Could not reach 'http://example.com'"}


def test_scan_blocked_by_robots_returns_400(client, monkeypatch):
    async def blocked(db, url, max_pages, ignore_robots):
        raise ScanBlockedByRobots(f"robots.txt disallows the scan target '{url}'")

    monkeypatch.setattr(main, 'run_scan_pipeline', blocked)
    http, _ = client

    resp = http.post('/scan', json={'url': 'http://example.com'})

    assert resp.status_code == 400
    assert 'robots.txt disallows' in resp.json()['detail']


def test_scan_error_is_sanitized(client, monkeypatch):
    async def boom(db, url, max_pages, ignore_robots):
        raise RuntimeError('secret: sqlite:////home/operator/hidden.db')

    monkeypatch.setattr(main, 'run_scan_pipeline', boom)
    http, _ = client
    resp = http.post('/scan', json={'url': 'http://127.0.0.1:1'})
    assert resp.status_code == 500
    detail = resp.json()['detail']
    assert detail.startswith('Internal server error')
    assert re.fullmatch(r'Internal server error \(ref: [0-9a-f]{8}\)', detail)
    assert 'secret' not in detail


def test_results_error_is_sanitized(client, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError('secret password=hunter2')

    monkeypatch.setattr(main, 'Database', boom)
    http, _ = client
    resp = http.get('/results')
    assert resp.status_code == 500
    detail = resp.json()['detail']
    assert detail.startswith('Internal server error')
    assert 'hunter2' not in detail


def test_scan_rejects_invalid_url(client):
    http, _ = client
    assert http.post('/scan', json={'url': 'not-a-url'}).status_code == 400


@pytest.mark.parametrize('url', [
    'http://example.com:99999',
    'http://example.com:abc',
    'http://example.com:0',
    'http://exa mple.com',
])
def test_scan_rejects_invalid_port_or_host(client, url):
    http, captured = client

    resp = http.post('/scan', json={'url': url})

    assert resp.status_code == 400
    assert resp.json() == {'detail': 'Invalid URL format'}
    assert 'max_pages' not in captured


def test_scan_accepts_ipv6_literal(client):
    http, captured = client

    resp = http.post('/scan', json={'url': 'http://[::1]:8000'})

    assert resp.status_code == 200
    assert 'max_pages' in captured


def test_scan_response_separates_info_notices(client, monkeypatch):
    async def fake_pipeline(db, url, max_pages, ignore_robots):
        return {
            'scan_id': 1,
            'html_page_count': 2,
            'issues': [
                {'severity': 'high'},
                {'severity': 'info'},
                {'severity': 'info'},
            ],
            'seo_grade': {'grade': 'A', 'score': 95},
            'resource_analysis': {},
        }

    monkeypatch.setattr(main, 'run_scan_pipeline', fake_pipeline)
    http, _ = client

    body = http.post('/scan', json={'url': 'http://example.com'}).json()

    assert body['total_issues'] == 1
    assert body['info_notices'] == 2


# --- /scans history ------------------------------------------------------------

def test_scans_empty_history(db_client):
    http, _ = db_client
    resp = http.get('/scans')
    assert resp.status_code == 200
    assert resp.json() == {'scans': []}


def test_scans_lists_created_scan_with_exact_contract(db_client):
    http, db = db_client
    _seed_scan(db, 'https://example.com', pages=2,
               issues={'high': 1, 'low': 2})
    resp = http.get('/scans')
    assert resp.status_code == 200
    entries = resp.json()['scans']
    assert len(entries) == 1
    entry = entries[0]
    assert set(entry) == {'scan_id', 'url', 'scan_date', 'grade_letter',
                          'grade_score', 'total_issues'}
    assert entry['scan_id'] == 1
    assert entry['url'] == 'https://example.com'
    assert entry['total_issues'] == 3
    assert datetime.fromisoformat(entry['scan_date']).utcoffset().total_seconds() == 0
    # The grade must match what the pipeline graded on: the stored page
    # count plus the severities persisted for the scan.
    expected = SEOGradeCalculator().calculate_grade(2, [
        {'severity': 'high'}, {'severity': 'low'}, {'severity': 'low'},
    ])
    assert entry['grade_letter'] == expected['grade']
    assert entry['grade_score'] == expected['score']


def test_scan_dates_are_utc_with_offset_including_legacy_rows(db_client):
    http, db = db_client
    scan_id = db.create_scan('https://legacy.example.com')
    # Rows written by older versions stored a naive local timestamp.
    db.conn.execute(
        'UPDATE scans SET timestamp = ? WHERE id = ?',
        ('2024-01-02T03:04:05', scan_id),
    )
    db.conn.commit()

    entry = http.get('/scans').json()['scans'][0]
    body = http.get(f'/results/{scan_id}').json()

    expected = datetime.fromisoformat(
        '2024-01-02T03:04:05').astimezone(timezone.utc).isoformat()
    assert entry['scan_date'] == expected
    assert body['scan']['timestamp'] == expected


def test_scans_excludes_info_notices_from_total(db_client):
    http, db = db_client
    # The stored total includes every row (the old behaviour); the endpoint
    # must recompute the actionable count from the issue severities.
    _seed_scan(db, 'https://example.com', pages=2,
               issues={'high': 1, 'info': 3})

    entry = http.get('/scans').json()['scans'][0]

    assert entry['total_issues'] == 1


def test_results_recompute_total_issues_and_info_notices(db_client):
    http, db = db_client
    scan_id = _seed_scan(db, 'https://example.com', pages=2,
                         issues={'medium': 2, 'info': 1})

    body = http.get(f'/results/{scan_id}').json()

    assert len(body['issues']) == 3
    assert body['scan']['total_issues'] == 2
    assert body['scan']['info_notices'] == 1


def test_scans_ordered_newest_first(db_client):
    http, db = db_client
    first = _seed_scan(db, 'https://first.example.com', 1, {})
    second = _seed_scan(db, 'https://second.example.com', 1, {})
    third = _seed_scan(db, 'https://third.example.com', 1, {})
    resp = http.get('/scans')
    assert [e['scan_id'] for e in resp.json()['scans']] == [third, second, first]


def test_scans_limit_returns_newest_n(db_client):
    http, db = db_client
    _seed_scan(db, 'https://old.example.com', 1, {})
    _seed_scan(db, 'https://middle.example.com', 1, {})
    newest = _seed_scan(db, 'https://new.example.com', 1, {})
    resp = http.get('/scans', params={'limit': 2})
    entries = resp.json()['scans']
    assert len(entries) == 2
    assert entries[0]['scan_id'] == newest
    assert entries[0]['url'] == 'https://new.example.com'


def test_scans_limit_is_clamped_into_valid_range(db_client):
    http, db = db_client
    _seed_scan(db, 'https://only.example.com', 1, {})
    assert len(http.get('/scans', params={'limit': 0}).json()['scans']) == 1
    assert len(http.get('/scans', params={'limit': -5}).json()['scans']) == 1


def test_scans_rejects_non_integer_limit(db_client):
    http, _ = db_client
    assert http.get('/scans', params={'limit': 'many'}).status_code == 422


def test_scans_respects_optional_api_key(db_client, monkeypatch):
    monkeypatch.setenv('SEO_PRISM_API_KEY', 'sekrit')
    http, db = db_client
    _seed_scan(db, 'https://example.com', 1, {})
    assert http.get('/scans').status_code == 401
    assert http.get('/scans', headers={'X-API-Key': 'sekrit'}).status_code == 200
