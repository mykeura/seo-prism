# SPDX-License-Identifier: AGPL-3.0-only
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
