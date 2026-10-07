# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
Shared fixtures and configuration for pytest tests.
"""
import pytest
import sqlite3
import tempfile
import os
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Initialize database with schema
    db = Database(db_path=path)
    
    yield db
    
    # Cleanup
    db.close()
    os.unlink(path)


@pytest.fixture
def sample_scan_id(temp_db):
    """Create a sample scan ID for testing."""
    scan_id = temp_db.create_scan('https://example.com')
    return scan_id


@pytest.fixture
def sample_page_data():
    """Sample page data for testing."""
    return {
        'url': 'https://example.com/page',
        'status': 200,
        'html': '<html><head><title>Test Page</title></head><body><h1>Test</h1></body></html>',
        'links': ['https://example.com/page2', 'https://external.com']
    }


@pytest.fixture
def sample_crawled_pages():
    """Sample crawled pages for testing."""
    return [
        {
            'url': 'https://example.com',
            'status': 200,
            'html': '<html><head><title>Home</title><meta name="description" content="Home page"></head><body><h1>Welcome</h1></body></html>',
            'links': ['https://example.com/about', 'https://example.com/contact']
        },
        {
            'url': 'https://example.com/about',
            'status': 200,
            'html': '<html><head><title>About</title><meta name="description" content="About page"></head><body><h1>About Us</h1></body></html>',
            'links': ['https://example.com']
        },
        {
            'url': 'https://example.com/contact',
            'status': 404,
            'html': None,
            'links': []
        }
    ]


@pytest.fixture
def sample_html_with_broken_links():
    """HTML sample with broken links."""
    return '''
    <html>
        <head><title>Test</title></head>
        <body>
            <a href="https://example.com/valid">Valid Link</a>
            <a href="https://example.com/404">Broken Link</a>
            <a href="https://external.com/broken">External Broken</a>
        </body>
    </html>
    '''


@pytest.fixture
def sample_html_missing_meta():
    """HTML sample missing meta tags."""
    return '''
    <html>
        <head></head>
        <body><h1>Test</h1></body>
    </html>
    '''


@pytest.fixture
def sample_html_duplicate_content():
    """HTML sample with duplicate content."""
    return '''
    <html>
        <head><title>Duplicate Title</title><meta name="description" content="Duplicate Description"></head>
        <body><h1>Test</h1></body>
    </html>
    '''


@pytest.fixture
def sample_html_h1_issues():
    """HTML sample with H1 issues."""
    return '''
    <html>
        <head><title>Test</title></head>
        <body>
            <h1>First H1</h1>
            <h1>Second H1</h1>
            <h2>Subheading</h2>
        </body>
    </html>
    '''


@pytest.fixture
def sample_html_invalid_hierarchy():
    """HTML sample with invalid header hierarchy."""
    return '''
    <html>
        <head><title>Test</title></head>
        <body>
            <h1>Main</h1>
            <h3>Skipped H2</h3>
            <h2>Invalid Order</h2>
        </body>
    </html>
    '''


@pytest.fixture
def sample_html_images_no_alt():
    """HTML sample with images missing alt tags."""
    return '''
    <html>
        <head><title>Test</title></head>
        <body>
            <img src="image1.jpg" />
            <img src="image2.jpg" alt="" />
            <img src="image3.jpg" alt="Short" />
        </body>
    </html>
    '''


@pytest.fixture
def sample_html_meta_robots():
    """HTML sample with meta robots."""
    return '''
    <html>
        <head>
            <title>Test</title>
            <meta name="robots" content="noindex, nofollow">
        </head>
        <body><h1>Test</h1></body>
    </html>
    '''


@pytest.fixture
def sample_html_canonical():
    """HTML sample with canonical tag."""
    return '''
    <html>
        <head>
            <title>Test</title>
            <link rel="canonical" href="https://example.com/canonical">
        </head>
        <body><h1>Test</h1></body>
    </html>
    '''


@pytest.fixture
def sample_html_hreflang():
    """HTML sample with hreflang tags."""
    return '''
    <html>
        <head>
            <title>Test</title>
            <link rel="alternate" hreflang="en" href="https://example.com/en">
            <link rel="alternate" hreflang="es" href="https://example.com/es">
        </head>
        <body><h1>Test</h1></body>
    </html>
    '''


@pytest.fixture
def sample_html_structured_data():
    """HTML sample with structured data."""
    return '''
    <html>
        <head>
            <title>Test</title>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": "Test Article"
            }
            </script>
        </head>
        <body><h1>Test</h1></body>
    </html>
    '''