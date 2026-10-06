# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

from urllib.parse import urlparse, urlunparse
from typing import Tuple, Optional


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
            # Default to http if no scheme provided
            parsed = urlparse(f"http://{user_input}")
        
        if not parsed.netloc:
            raise ValueError("Invalid URL: missing network location")
        
        # Extract domain and port
        domain = parsed.hostname
        if not domain:
            raise ValueError("Invalid URL: missing hostname")
        
        # Validate hostname format - must contain at least one dot or be localhost
        # or be a valid IP address
        if domain != 'localhost' and '.' not in domain:
            # Check if it's a valid IP address
            import re
            ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            if not re.match(ip_pattern, domain):
                raise ValueError("Invalid URL: invalid hostname format")
        
        port = parsed.port
        if port is None:
            port = 80 if parsed.scheme == 'http' else 443
        
        # Construct domain:port string
        domain_with_port = f"{domain}:{port}" if port not in [80, 443] else domain
        
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
        
        # Check for localhost variants
        if domain in ['localhost', '127.0.0.1', '::1']:
            return True
        
        # Check for .test or .local TLDs
        if domain.endswith('.test') or domain.endswith('.local'):
            return True
        
        # Check for IP addresses in private ranges
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
        return all([parsed.scheme in ['http', 'https'], parsed.netloc])
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
    
    # Remove fragment
    parsed = parsed._replace(fragment='')
    
    # Remove trailing slash from path (the root '/' also collapses to '',
    # so 'http://example.com' and 'http://example.com/' are the same page)
    if parsed.path.endswith('/'):
        parsed = parsed._replace(path=parsed.path.rstrip('/'))
    
    return urlunparse(parsed)