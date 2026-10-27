# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""Tests for the DNS-resolution private-target guard."""
import asyncio
import http.server
import socket
import threading

import pytest

import core.net_guard as net_guard
from core.crawler import Crawler
from core.net_guard import (
    NetworkGuard,
    build_connector,
    ensure_public_host,
    ensure_public_url,
)


def _addrinfos(addresses, family=socket.AF_INET):
    def sockaddr(addr):
        return (addr, 0) if family == socket.AF_INET else (addr, 0, 0, 0)

    return [(family, socket.SOCK_STREAM, 6, '', sockaddr(a)) for a in addresses]


def _run_with_resolver(url, addresses=None, family=socket.AF_INET, error=None):
    """Run the guard with loop.getaddrinfo stubbed inside the same loop."""
    async def main():
        loop = asyncio.get_running_loop()

        async def fake_getaddrinfo(host, port, *args, **kwargs):
            if error is not None:
                raise error
            return _addrinfos(addresses, family)

        loop.getaddrinfo = fake_getaddrinfo
        await ensure_public_url(url)

    asyncio.run(main())


def test_rejects_localhost():
    with pytest.raises(ValueError, match='non-public'):
        asyncio.run(ensure_public_url('http://localhost:8000/'))


def test_rejects_loopback_literal():
    with pytest.raises(ValueError, match='non-public'):
        asyncio.run(ensure_public_url('http://127.0.0.1:8080/'))


def test_rejects_ipv6_loopback_literal():
    with pytest.raises(ValueError, match='non-public'):
        asyncio.run(ensure_public_url('http://[::1]:8080/'))


def test_rejects_link_local_metadata_endpoint():
    with pytest.raises(ValueError, match='non-public'):
        asyncio.run(ensure_public_url('http://169.254.169.254/latest/meta-data/'))


def test_rejects_unique_local_ipv6_literal():
    with pytest.raises(ValueError, match='non-public'):
        asyncio.run(ensure_public_url('http://[fd12:3456:789a::1]/'))


def test_rejects_name_resolving_to_private_ip():
    with pytest.raises(ValueError, match='non-public'):
        _run_with_resolver('http://intranet.internal.example/', ['10.0.0.5'])


def test_rejects_when_any_resolved_ip_is_private():
    with pytest.raises(ValueError, match='non-public'):
        _run_with_resolver('http://mixed.example/', ['93.184.216.34', '192.168.1.10'])


def test_accepts_name_resolving_to_public_ip():
    _run_with_resolver('http://example.com/', ['93.184.216.34'])


def test_accepts_public_ipv6():
    _run_with_resolver('http://example.com/',
                       ['2606:2800:220:1:248:1893:25c8:1946'],
                       family=socket.AF_INET6)


def test_rejects_unresolvable_host():
    with pytest.raises(ValueError, match='Could not resolve'):
        _run_with_resolver('http://nope.invalid/',
                           error=socket.gaierror(8, 'Name unknown'))


def test_rejects_url_without_hostname():
    with pytest.raises(ValueError, match='hostname'):
        asyncio.run(ensure_public_url('not-a-url'))


@pytest.mark.parametrize('address', [
    '::ffff:127.0.0.1',
    '224.0.0.1',
    '100.64.0.1',
    '0.0.0.0',
])
def test_rejects_other_non_public_literals(address):
    with pytest.raises(ValueError, match='non-public'):
        asyncio.run(ensure_public_host(address))


def test_network_guard_disabled_allows_private_targets():
    asyncio.run(NetworkGuard(False).check_url('http://127.0.0.1:8000/'))


def test_network_guard_from_env(monkeypatch):
    monkeypatch.delenv('SEO_PRISM_BLOCK_PRIVATE_TARGETS', raising=False)
    assert NetworkGuard.from_env().enabled is False

    monkeypatch.setenv('SEO_PRISM_BLOCK_PRIVATE_TARGETS', '1')
    assert NetworkGuard.from_env().enabled is True


def test_guarded_connector_blocks_ip_literals_before_connecting():
    async def main():
        connector = build_connector(NetworkGuard(True))
        try:
            with pytest.raises(ValueError, match='non-public'):
                await connector._resolve_host('169.254.169.254', 80)
        finally:
            await connector.close()

    asyncio.run(main())


class _RedirectToMetadata(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        self.send_response(302)
        self.send_header('Location', 'http://169.254.169.254/latest/meta-data/')
        self.end_headers()


def test_redirect_to_private_ip_is_blocked_by_the_connector(monkeypatch):
    """The initial host is allowed; the redirect target must be rejected."""
    def fake_is_non_public(address):
        return not str(address).startswith('127.0.0.1')

    monkeypatch.setattr(net_guard, '_is_non_public', fake_is_non_public)

    server = http.server.ThreadingHTTPServer(
        ('127.0.0.1', 0), _RedirectToMetadata)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_address[1]}/'

    async def main():
        async with Crawler(base, ignore_robots=True,
                           guard=NetworkGuard(True)) as crawler:
            return await crawler.crawl(max_pages=1)

    try:
        results = asyncio.run(main())
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

    assert len(results) == 1
    assert results[0]['status'] == 0
    assert 'non-public' in results[0]['error']
