# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""DNS-resolution guard for user-supplied scan targets.

Opt-in SSRF protection for hosted deployments: a target URL whose host
resolves to any non-public address is rejected before crawling. It must
stay opt-in because scanning your own localhost is a product feature.
"""

import asyncio
import ipaddress
import socket
from urllib.parse import urlparse


def _is_non_public(address: str) -> bool:
    ip = ipaddress.ip_address(address)
    # is_private also covers unique-local IPv6 (fc00::/7) and 0.0.0.0;
    # is_link_local covers the cloud metadata endpoint 169.254.169.254.
    return ip.is_private or ip.is_loopback or ip.is_link_local


async def ensure_public_url(url: str) -> None:
    """Resolve url's host and raise ValueError if any address is non-public."""
    host = urlparse(url).hostname
    if not host:
        raise ValueError("URL has no hostname to resolve")

    loop = asyncio.get_running_loop()
    try:
        infos = await loop.getaddrinfo(host, None)
    except OSError as exc:
        raise ValueError(f"Could not resolve host '{host}'") from exc

    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if _is_non_public(str(ip)):
            raise ValueError(
                f"Host '{host}' resolves to a non-public address ({ip}); "
                "this instance blocks private targets"
            )
