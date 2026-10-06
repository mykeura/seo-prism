# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
Unit tests for url_utils module.
"""
import pytest
from core.url_utils import parse_target_url, is_local, validate_url, resolve_relative_url, normalize_url


class TestParseTargetUrl:
    """Tests for parse_target_url function."""
    
    def test_parse_http_url(self):
        """Test parsing a standard HTTP URL."""
        domain, port, scheme = parse_target_url("http://example.com")
        assert domain == "example.com"
        assert port == 80
        assert scheme == "http"
    
    def test_parse_https_url(self):
        """Test parsing a standard HTTPS URL."""
        domain, port, scheme = parse_target_url("https://example.com")
        assert domain == "example.com"
        assert port == 443
        assert scheme == "https"
    
    def test_parse_url_with_port(self):
        """Test parsing a URL with custom port."""
        domain, port, scheme = parse_target_url("http://localhost:3000")
        assert domain == "localhost:3000"
        assert port == 3000
        assert scheme == "http"
    
    def test_parse_url_without_scheme(self):
        """Test parsing URL without scheme (defaults to http)."""
        domain, port, scheme = parse_target_url("example.com")
        assert domain == "example.com"
        assert port == 80
        assert scheme == "http"
    
    def test_parse_invalid_url(self):
        """Test parsing an invalid URL raises ValueError."""
        with pytest.raises(ValueError):
            parse_target_url("not a url")


class TestIsLocal:
    """Tests for is_local function."""
    
    def test_localhost(self):
        """Test localhost is detected as local."""
        assert is_local("http://localhost:3000") is True
    
    def test_127_0_0_1(self):
        """Test 127.0.0.1 is detected as local."""
        assert is_local("http://127.0.0.1:8080") is True
    
    def test_test_tld(self):
        """Test .test TLD is detected as local."""
        assert is_local("http://example.test") is True
    
    def test_local_tld(self):
        """Test .local TLD is detected as local."""
        assert is_local("http://example.local") is True
    
    def test_private_ip_192_168(self):
        """Test 192.168.x.x is detected as local."""
        assert is_local("http://192.168.1.1") is True
    
    def test_private_ip_10(self):
        """Test 10.x.x.x is detected as local."""
        assert is_local("http://10.0.0.1") is True
    
    def test_private_ip_172(self):
        """Test 172.16-31.x.x is detected as local."""
        assert is_local("http://172.16.0.1") is True
        assert is_local("http://172.31.0.1") is True
        assert is_local("http://172.15.0.1") is False  # Out of range
    
    def test_public_url(self):
        """Test public URLs are not detected as local."""
        assert is_local("https://example.com") is False
        assert is_local("https://google.com") is False


class TestValidateUrl:
    """Tests for validate_url function."""
    
    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        assert validate_url("http://example.com") is True
    
    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        assert validate_url("https://example.com") is True
    
    def test_valid_url_with_port(self):
        """Test valid URL with port."""
        assert validate_url("http://localhost:3000") is True
    
    def test_invalid_url_no_scheme(self):
        """Test URL without scheme is invalid."""
        assert validate_url("example.com") is False
    
    def test_invalid_url_no_netloc(self):
        """Test URL without network location is invalid."""
        assert validate_url("http://") is False
    
    def test_invalid_scheme(self):
        """Test URL with invalid scheme."""
        assert validate_url("ftp://example.com") is False
    
    def test_invalid_format(self):
        """Test completely invalid format."""
        assert validate_url("not a url") is False


class TestResolveRelativeUrl:
    """Tests for resolve_relative_url function."""
    
    def test_resolve_absolute_url(self):
        """Test resolving an absolute URL returns it unchanged."""
        result = resolve_relative_url("http://example.com/page", "https://other.com/page2")
        assert result == "https://other.com/page2"
    
    def test_resolve_relative_path(self):
        """Test resolving a relative path."""
        result = resolve_relative_url("http://example.com/dir/", "page.html")
        assert result == "http://example.com/dir/page.html"
    
    def test_resolve_relative_with_dots(self):
        """Test resolving relative path with dots."""
        result = resolve_relative_url("http://example.com/dir/subdir/", "../page.html")
        assert result == "http://example.com/dir/page.html"
    
    def test_resolve_root_relative(self):
        """Test resolving root-relative path."""
        result = resolve_relative_url("http://example.com/dir/", "/page.html")
        assert result == "http://example.com/page.html"


class TestNormalizeUrl:
    """Tests for normalize_url function."""
    
    def test_remove_trailing_slash(self):
        """Test removing trailing slash."""
        assert normalize_url("http://example.com/page/") == "http://example.com/page"
    
    def test_root_slash_collapses(self):
        """Root '/' normalizes to '' so 'x.com' and 'x.com/' are the same page."""
        assert normalize_url("http://example.com/") == "http://example.com"
        assert normalize_url("http://example.com") == "http://example.com"
    
    def test_remove_fragment(self):
        """Test removing fragment."""
        assert normalize_url("http://example.com/page#section") == "http://example.com/page"
    
    def test_remove_trailing_slash_and_fragment(self):
        """Test removing both trailing slash and fragment."""
        assert normalize_url("http://example.com/page/#section") == "http://example.com/page"
    
    def test_keep_query_string(self):
        """Test keeping query string."""
        assert normalize_url("http://example.com/page?param=value") == "http://example.com/page?param=value"