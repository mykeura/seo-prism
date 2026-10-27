# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
Tests for the MCP server.

Covers the real stdio protocol handshake (initialize -> tools/list ->
tools/call) plus the seo_scan tool behaviour against a local HTTP fixture.
"""
import asyncio
import functools
import http.server
import json
import sys
import threading
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import mcp_server
from core.pipeline import ScanTargetUnreachable


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@pytest.fixture
def static_site(tmp_path):
    """Serve tmp_path over HTTP on an ephemeral port."""
    handler = functools.partial(_QuietHandler, directory=str(tmp_path))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_address[1]}', tmp_path
    server.shutdown()
    thread.join()


def _write(root, name, content):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_seo_scan_tool_returns_results(static_site):
    base, tmp_path = static_site
    _write(tmp_path, 'index.html',
           '<html><head><title>Home</title></head><body>'
           '<a href="/missing">broken</a></body></html>')
    _write(tmp_path, 'robots.txt', 'User-agent: *\nAllow: /\n')

    result = asyncio.run(mcp_server.seo_scan(base, max_pages=5))

    assert 'error' not in result
    assert set(result) == {'scan', 'issues', 'seo_grade', 'resource_analysis'}
    assert result['scan']['url'] == base
    assert result['scan']['pages_analyzed'] >= 1
    broken = [i for i in result['issues'] if i['issue_type'] == 'broken_link']
    assert any('/missing' in i['url'] for i in broken)


def test_seo_scan_tool_rejects_invalid_url():
    result = asyncio.run(mcp_server.seo_scan('not-a-url'))
    assert 'error' in result


class _FakeDB:
    def close(self):
        pass


def test_seo_scan_clamps_only_when_env_limit_is_set(monkeypatch):
    captured = {}

    async def fake_pipeline(db, url, max_pages, ignore_robots, guard=None):
        captured['max_pages'] = max_pages
        return {'scan_id': 1, 'html_page_count': 1, 'issues': [],
                'seo_grade': {'grade': 'A', 'score': 95}, 'resource_analysis': {}}

    monkeypatch.setattr(mcp_server, 'Database', lambda *a, **k: _FakeDB())
    monkeypatch.setattr(mcp_server, 'run_scan_pipeline', fake_pipeline)
    monkeypatch.delenv('SEO_PRISM_MAX_PAGES_LIMIT', raising=False)

    asyncio.run(mcp_server.seo_scan('http://127.0.0.1:1', max_pages=99999))
    assert captured['max_pages'] == 99999

    monkeypatch.setenv('SEO_PRISM_MAX_PAGES_LIMIT', '30')
    asyncio.run(mcp_server.seo_scan('http://127.0.0.1:1', max_pages=99999))
    assert captured['max_pages'] == 30

    asyncio.run(mcp_server.seo_scan('http://127.0.0.1:1', max_pages=0))
    assert captured['max_pages'] == 1


def test_seo_scan_blocks_private_target_when_guard_enabled(monkeypatch):
    calls = []

    async def fake_pipeline(db, url, max_pages, ignore_robots, guard=None):
        calls.append(url)
        return {'scan_id': 1, 'html_page_count': 1, 'issues': [],
                'seo_grade': {'grade': 'A', 'score': 95}, 'resource_analysis': {}}

    monkeypatch.setenv('SEO_PRISM_BLOCK_PRIVATE_TARGETS', '1')
    monkeypatch.setattr(mcp_server, 'Database', lambda *a, **k: _FakeDB())
    monkeypatch.setattr(mcp_server, 'run_scan_pipeline', fake_pipeline)

    result = asyncio.run(mcp_server.seo_scan('http://127.0.0.1:1'))

    assert 'error' in result
    assert 'non-public' in result['error']
    assert calls == []


def test_seo_scan_returns_error_when_target_is_unreachable(monkeypatch):
    async def unreachable(db, url, max_pages, ignore_robots, guard=None):
        raise ScanTargetUnreachable(f"Could not reach '{url}'")

    monkeypatch.setattr(mcp_server, 'Database', lambda *a, **k: _FakeDB())
    monkeypatch.setattr(mcp_server, 'run_scan_pipeline', unreachable)

    result = asyncio.run(mcp_server.seo_scan('http://example.com'))

    assert result == {'error': "Could not reach 'http://example.com'"}


def test_seo_scan_reports_actionable_totals_separately(monkeypatch):
    async def fake_pipeline(db, url, max_pages, ignore_robots, guard=None):
        return {
            'scan_id': 1,
            'html_page_count': 1,
            'issues': [{'severity': 'high'}, {'severity': 'info'}],
            'seo_grade': {'grade': 'A', 'score': 95},
            'resource_analysis': {},
        }

    monkeypatch.setattr(mcp_server, 'Database', lambda *a, **k: _FakeDB())
    monkeypatch.setattr(mcp_server, 'run_scan_pipeline', fake_pipeline)

    result = asyncio.run(mcp_server.seo_scan('http://example.com'))

    assert result['scan']['total_issues'] == 1
    assert result['scan']['info_notices'] == 1


def test_mcp_stdio_protocol():
    """Drive the real server over stdio: initialize, tools/list, tools/call."""
    backend_dir = Path(__file__).parent.parent
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(backend_dir / 'mcp_server.py')],
        cwd=str(backend_dir),
    )

    async def _session():
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await session.list_tools()

    tools = asyncio.run(_session())
    names = [t.name for t in tools.tools]
    assert names == ['seo_scan']
    schema = tools.tools[0].input_schema
    assert 'url' in schema['properties']
    assert 'url' in schema['required']


def test_mcp_stdio_call_invalid_url():
    """tools/call over real stdio returns the error payload, not a crash."""
    backend_dir = Path(__file__).parent.parent
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(backend_dir / 'mcp_server.py')],
        cwd=str(backend_dir),
    )

    async def _session():
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await session.call_tool('seo_scan', {'url': 'nope'})

    result = asyncio.run(_session())
    text = result.content[0].text
    assert 'error' in json.loads(text) or 'error' in text
