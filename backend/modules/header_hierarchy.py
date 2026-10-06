# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

from bs4 import BeautifulSoup
import re


def analyze_header_hierarchy(soup: BeautifulSoup, url: str):
    """
    Analyzes the header hierarchy in an HTML page.
    Verifies if headers follow a logical structure (H1 -> H2 -> H3, etc.)
    """
    issues = []
    
    # Find all headers in order
    headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    if not headers:
        return issues
    
    header_levels = []
    for header in headers:
        # Extract the header number (h1 -> 1, h2 -> 2, etc.)
        level = int(re.search(r'h(\d)', header.name.lower()).group(1))
        header_levels.append(level)
    
    # Check for invalid hierarchy
    for i in range(1, len(header_levels)):
        current_level = header_levels[i]
        previous_level = header_levels[i-1]
        
        # If the level jump is greater than 1 (e.g., from H1 to H3), it's an error
        if current_level > previous_level + 1:
            issues.append({
                'issue_type': 'invalid_header_hierarchy',
                'url': url,
                'source_page': url,
                'description': f'Invalid header hierarchy: H{previous_level} -> H{current_level} (expected H{previous_level+1} or lower)',
                'severity': 'medium'
            })
    
    # Optional: check for backward level jumps that might be confusing
    # For example: H1 -> H2 -> H4 -> H2 (the second H2 is fine, but can be reviewed)
    
    return issues