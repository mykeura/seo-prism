# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import ipaddress
import re
from urllib.parse import urlparse, urlunparse
from typing import Tuple, Optional


_DNS_LABEL = re.compile(r'^[a-z0-9-]+$')


def _validate_hostname(domain: str) -> str:
    """Validate an IP literal or DNS hostname and return its normalized form."""
    try:
        ipaddress.ip_address(domain)
    except ValueError:
        pass
    else:
        return domain

    try:
        ascii_domain = domain.encode('idna').decode('ascii').lower()
    except UnicodeError as exc:
        raise ValueError("Invalid URL: invalid hostname format") from exc

    ascii_domain = ascii_domain.rstrip('.')
    if not ascii_domain or len(ascii_domain) > 253:
        raise ValueError("Invalid URL: invalid hostname format")

    labels = ascii_domain.split('.')
    if any(
        not label
        or len(label) > 63
        or label.startswith('-')
        or label.endswith('-')
        or not _DNS_LABEL.fullmatch(label)
        for label in labels
    ):
        raise ValueError("Invalid URL: invalid hostname format")

    # Keep the historical rule: single-label hosts are only localhost.
    if len(labels) == 1 and labels[0] != 'localhost':
        raise ValueError("Invalid URL: invalid hostname format")

    return ascii_domain


def parse_target_url(user_input: str) -> Tuple[str, int, str]:
    """
    Parse a target URL and extract domain, port, and scheme.
    
    Args:
        user_input: URL string (e.g., "http://localhost:3000", "https://example.com")
    
    Returns:
        Tuple of (domain_with_port, port, scheme)
    
    Raises:
        ValueError: If URL is invalid
    """
    try:
        parsed = urlparse(user_input)
        
        if not parsed.scheme:
            parsed = urlparse(f"http://{user_input}")
        
        if parsed.scheme not in ('http', 'https'):
            raise ValueError("Invalid URL: unsupported scheme")

        if not parsed.netloc:
            raise ValueError("Invalid URL: missing network location")
        
        domain = parsed.hostname
        if not domain:
            raise ValueError("Invalid URL: missing hostname")

        domain = _validate_hostname(domain)
        
        port = parsed.port
        if port is None:
            port = 80 if parsed.scheme == 'http' else 443
        if not 1 <= port <= 65535:
            raise ValueError("Invalid URL: port must be between 1 and 65535")

        # IPv6 literals need brackets when rebuilt with a port.
        host = f'[{domain}]' if ':' in domain else domain
        domain_with_port = f"{host}:{port}" if port not in (80, 443) else host
        
        return domain_with_port, port, parsed.scheme
    
    except Exception as e:
        raise ValueError(f"Invalid URL format: {e}")


def is_local(url: str) -> bool:
    """
    Check if a URL is local (localhost, 127.0.0.1, .test, .local).
    
    Args:
        url: URL string to check
    
    Returns:
        True if URL is local, False otherwise
    """
    try:
        parsed = urlparse(url)
        domain = parsed.hostname.lower() if parsed.hostname else ""
        
        if domain in ['localhost', '127.0.0.1', '::1']:
            return True
        
        if domain.endswith('.test') or domain.endswith('.local'):
            return True
        
        if domain.startswith('192.168.') or domain.startswith('10.'):
            return True
        
        if domain.startswith('172.'):
            parts = domain.split('.')
            if len(parts) >= 2 and 16 <= int(parts[1]) <= 31:
                return True
        
        return False
    
    except Exception:
        return False


def validate_url(url: str) -> bool:
    """
    Validate if a URL has a proper format.
    
    Args:
        url: URL string to validate
    
    Returns:
        True if URL is valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            return False
        # Accessing .port raises on non-numeric/out-of-range ports and
        # parse_target_url validates the hostname (including IPv6 literals).
        parse_target_url(url)
        return True
    except Exception:
        return False


def resolve_relative_url(base_url: str, relative_url: str) -> str:
    """
    Resolve a relative URL against a base URL.
    
    Args:
        base_url: The base URL to resolve against
        relative_url: The relative or absolute URL to resolve
    
    Returns:
        Absolute URL string
    """
    from urllib.parse import urljoin
    
    return urljoin(base_url, relative_url)


def normalize_url(url: str) -> str:
    """
    Normalize a URL by removing trailing slashes and fragments.
    
    Args:
        url: URL string to normalize
    
    Returns:
        Normalized URL string
    """
    parsed = urlparse(url)
    
    parsed = parsed._replace(fragment='')
    
    # Remove trailing slash from path (the root '/' also collapses to '',
    # so 'http://example.com' and 'http://example.com/' are the same page)
    if parsed.path.endswith('/'):
        parsed = parsed._replace(path=parsed.path.rstrip('/'))
    
    return urlunparse(parsed)