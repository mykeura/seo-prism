# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""A target that cannot be scanned must fail, not become an F report.

Historic bug: connection errors were stored as status 0, the page count
became zero and the pipeline emitted an F grade with four missing-file
issues, an HTTP 200 and a zero exit code.
"""
import asyncio
import contextlib
import http.server
import socket
import threading

import pytest

from core.pipeline import (
    ScanBlockedByRobots,
    ScanError,
    ScanTargetUnreachable,
    run_scan_pipeline,
)
from database import Database


class _Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        self.server.requests.append(path)
        route = self.server.routes.get(path)
        if route is None:
            body = '<html><head><title>Not found</title></head><body>404</body></html>'
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body.encode())
            return

        status, headers, body = route
        self.send_response(status)
        for name, value in headers.items():
            self.send_header(name, value)
        if body is not None:
            self.send_header('Content-Length', str(len(body.encode())))
        self.end_headers()
        if body:
            self.wfile.write(body.encode())


@contextlib.contextmanager
def _site(routes):
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), _Handler)
    server.routes = routes
    server.requests = []
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_address[1]}', server
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def _closed_port():
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def _html(title='Home'):
    return (200, {'Content-Type': 'text/html; charset=utf-8'},
            f'<html><head><title>{title}</title></head><body><h1>{title}</h1></body></html>')


def test_unreachable_target_raises_and_creates_no_scan():
    db = Database(':memory:')
    try:
        with pytest.raises(ScanTargetUnreachable, match='Could not reach'):
            asyncio.run(run_scan_pipeline(
                db, f'http://127.0.0.1:{_closed_port()}/', 1, True))
        assert db.get_latest_scan() is None
        assert db.list_scans() == []
    finally:
        db.close()


def test_root_404_is_a_target_error_not_a_graded_report():
    with _site({}) as (base, _):
        db = Database(':memory:')
        try:
            with pytest.raises(ScanError, match='HTTP 404'):
                asyncio.run(run_scan_pipeline(db, base, 1, True))
            assert db.get_latest_scan() is None
        finally:
            db.close()


def test_non_html_target_is_rejected():
    routes = {'/': (200, {'Content-Type': 'application/json'}, '{"ok": true}')}
    with _site(routes) as (base, _):
        db = Database(':memory:')
        try:
            with pytest.raises(ScanError, match='No HTML content'):
                asyncio.run(run_scan_pipeline(db, base, 1, True))
            assert db.get_latest_scan() is None
        finally:
            db.close()


def test_robots_blocking_the_scan_root_is_reported():
    routes = {
        '/robots.txt': (200, {'Content-Type': 'text/plain'},
                        'User-agent: *\nDisallow: /\n'),
        '/': _html(),
    }
    with _site(routes) as (base, server):
        db = Database(':memory:')
        try:
            with pytest.raises(ScanBlockedByRobots, match='robots.txt disallows'):
                asyncio.run(run_scan_pipeline(db, base, 1, False))
            assert db.get_latest_scan() is None
            assert '/' not in server.requests
        finally:
            db.close()


def test_guard_blocked_target_is_unreachable_and_not_graded(monkeypatch):
    monkeypatch.setenv('SEO_PRISM_BLOCK_PRIVATE_TARGETS', '1')
    db = Database(':memory:')
    try:
        with pytest.raises(ScanTargetUnreachable, match='non-public'):
            asyncio.run(run_scan_pipeline(
                db, 'http://127.0.0.1:1/', 1, True))
        assert db.get_latest_scan() is None
    finally:
        db.close()
