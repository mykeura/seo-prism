# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""The event loop must stay responsive while a scan analyses its pages."""

import asyncio
import contextlib
import functools
import http.server
import threading
import time

import httpx

import api.main as main
from database import Database
from modules.meta_tags import MetaTagsModule


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def test_health_responds_while_analysis_is_running(tmp_path, monkeypatch):
    (tmp_path / 'index.html').write_text(
        '<html><head><title>Home</title></head>'
        '<body><h1>Home</h1></body></html>'
    )
    handler = functools.partial(_QuietHandler, directory=str(tmp_path))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_address[1]}'

    monkeypatch.setattr(
        main, 'Database', lambda *a, **k: Database(str(tmp_path / 'scans.db')))

    started = threading.Event()
    analysis_started_at = {}

    def slow_analyze(self, scan_id, crawled_pages):
        # Simulates CPU-bound parsing that used to block the event loop.
        analysis_started_at['value'] = time.monotonic()
        started.set()
        time.sleep(1.0)
        return []

    monkeypatch.setattr(MetaTagsModule, 'analyze', slow_analyze)

    async def scenario():
        transport = httpx.ASGITransport(app=main.app)
        async with httpx.AsyncClient(
                transport=transport, base_url='http://test') as client:
            scan_task = asyncio.create_task(client.post(
                '/scan', json={'url': base, 'max_pages': 1}, timeout=30))
            try:
                assert await asyncio.to_thread(started.wait, 10)
                health = await client.get('/health', timeout=5)
                elapsed = time.monotonic() - analysis_started_at['value']
                scan = await scan_task
                return health, elapsed, scan
            finally:
                if not scan_task.done():
                    scan_task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await scan_task

    try:
        health, elapsed, scan = asyncio.run(scenario())
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

    assert health.status_code == 200
    assert health.json()['status'] == 'ok'
    # The health response must arrive long before the 1s analysis finishes;
    # if the module runs on the loop thread this is >= 1s.
    assert elapsed < 0.5
    assert scan.status_code == 200
