# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""DNS-resolution guard for user-supplied scan targets.

Opt-in SSRF protection for hosted deployments. The environment flag makes
the API, MCP server and CLI reject scan targets and redirect/resource hops
whose host resolves to a non-public address. It must stay opt-in because
scanning your own localhost is a product feature.

The guard is enforced both up-front (clear 400/error for the requested URL)
and inside the aiohttp connector, so redirects, external resources,
robots.txt and standard-file checks are covered too. We validate the
addresses returned by the resolver at connection time; we do not pin a
separate DNS resolution to the socket (residual DNS-rebinding risk).
"""

import asyncio
import ipaddress
import os
from typing import Optional
from urllib.parse import urlparse

import aiohttp

_CGNAT = ipaddress.ip_network("100.64.0.0/10")


def _is_non_public(address: str) -> bool:
    ip = ipaddress.ip_address(address)
    # IPv4-mapped IPv6 (::ffff:127.0.0.1) must be judged as its IPv4 form.
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    if ip.version == 4 and ip in _CGNAT:
        return True
    # is_private also covers unique-local IPv6 (fc00::/7) and 0.0.0.0;
    # is_link_local covers the cloud metadata endpoint 169.254.169.254.
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _reject_non_public(host: str, address) -> None:
    if _is_non_public(str(address)):
        raise ValueError(
            f"Host '{host}' resolves to a non-public address ({address}); "
            "this instance blocks private targets"
        )


async def ensure_public_host(host: str) -> None:
    """Validate a hostname or IP literal; raise ValueError when non-public."""
    normalized = (host or '').strip().strip('[]')
    if not normalized:
        raise ValueError("URL has no hostname to resolve")

    try:
        literal = ipaddress.ip_address(normalized)
    except ValueError:
        literal = None

    if literal is not None:
        _reject_non_public(normalized, literal)
        return

    loop = asyncio.get_running_loop()
    try:
        infos = await loop.getaddrinfo(normalized, None)
    except OSError as exc:
        raise ValueError(f"Could not resolve host '{normalized}'") from exc

    for info in infos:
        # IPv6 scoped addresses can carry a %zone suffix.
        address = info[4][0].split('%', 1)[0]
        _reject_non_public(normalized, address)


async def ensure_public_url(url: str) -> None:
    """Resolve url's host and raise ValueError if any address is non-public."""
    host = urlparse(url).hostname
    if not host:
        raise ValueError("URL has no hostname to resolve")
    await ensure_public_host(host)


class NetworkGuard:
    """Opt-in switch shared by the entry points and the HTTP connector."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    @classmethod
    def from_env(cls) -> "NetworkGuard":
        return cls(os.environ.get("SEO_PRISM_BLOCK_PRIVATE_TARGETS") == "1")

    async def check_url(self, url: str) -> None:
        if self.enabled:
            await ensure_public_url(url)

    async def check_host(self, host: str) -> None:
        if self.enabled:
            await ensure_public_host(host)


class _GuardedConnector(aiohttp.TCPConnector):
    """TCPConnector that validates every host before a connection is made.

    aiohttp resolves IP literals without calling the configured resolver,
    so overriding _resolve_host (instead of only wrapping the resolver) is
    what closes the ``http://169.254.169.254/`` bypass.
    """

    def __init__(self, guard: NetworkGuard, **kwargs):
        self._guard = guard
        super().__init__(**kwargs)

    async def _resolve_host(self, host: str, port: int, traces=None):
        await self._guard.check_host(host)
        return await super()._resolve_host(host, port, traces)


def build_connector(guard: Optional[NetworkGuard] = None,
                    **kwargs) -> aiohttp.TCPConnector:
    """Build a normal connector or a guarded one when the flag is active."""
    if guard is not None and guard.enabled:
        return _GuardedConnector(guard, **kwargs)
    return aiohttp.TCPConnector(**kwargs)
