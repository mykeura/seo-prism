# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

from typing import List, Dict
from bs4 import BeautifulSoup
from database import Database
import re


class ThinContentModule:
    """Module to detect pages with thin content (little content)."""
    
    # Minimum word count threshold for article content
    MIN_WORD_COUNT = 300
    
    # Minimum character count threshold for article content
    MIN_CHAR_COUNT = 1500
    
    def __init__(self, db: Database):
        """
        Initialize the Thin Content module.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def analyze(self, scan_id: int, crawled_pages: List[Dict]) -> List[Dict]:
        """
        Analyze crawled pages for thin content issues.
        
        Args:
            scan_id: Scan ID
            crawled_pages: List of crawled page results
        
        Returns:
            List of thin content issues
        """
        issues = []
        
        for page in crawled_pages:
            page_url = page['url']
            html = page.get('html')
            
            if not html:
                continue
            
            # Parse its own copy: _extract_article_content decomposes nodes,
            # which must not corrupt the cached soup shared with other modules
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract article content excluding title
            article_content = self._extract_article_content(soup)
            
            # Count words and characters
            word_count = len(article_content.split())
            char_count = len(article_content)
            
            # Check if content is too short
            if word_count < self.MIN_WORD_COUNT or char_count < self.MIN_CHAR_COUNT:
                severity = 'high' if word_count < 100 else 'medium'
                
                issue = {
                    'issue_type': 'thin_content',
                    'url': page_url,
                    'source_page': page_url,
                    'description': f'Page has thin content. Word count: {word_count} (minimum: {self.MIN_WORD_COUNT}), Character count: {char_count} (minimum: {self.MIN_CHAR_COUNT})',
                    'severity': severity
                }
                issues.append(issue)
                
                # Add to database
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='thin_content',
                    url=page_url,
                    source_page=page_url,
                    description=f'Page has thin content. Word count: {word_count} (minimum: {self.MIN_WORD_COUNT}), Character count: {char_count} (minimum: {self.MIN_CHAR_COUNT})',
                    severity=severity
                )
        
        return issues
    
    def _extract_article_content(self, soup: BeautifulSoup) -> str:
        """
        Extract article content from HTML, excluding title and non-content elements.
        
        Args:
            soup: BeautifulSoup object
        
        Returns:
            Cleaned article content text
        """
        # Remove non-content elements
        for element in soup.find_all(['nav', 'header', 'footer', 'aside', 'script', 'style', 
                                      'noscript', 'iframe', 'svg', 'form', 'button', 'input',
                                      'textarea', 'select', 'option', 'label', 'fieldset']):
            element.decompose()
        
        # Remove title, h1 elements (they are not article content)
        for element in soup.find_all(['title', 'h1']):
            element.decompose()
        
        # Try to find main content area
        main_content = (
            soup.find('main') or 
            soup.find('article') or 
            soup.find('div', {'class': re.compile(r'content|article|post|entry', re.I)}) or
            soup.find('div', {'id': re.compile(r'content|article|post|entry', re.I)}) or
            soup.body
        )
        
        if main_content:
            # Get all text content
            text = main_content.get_text(separator=' ', strip=True)
        else:
            # Fallback to entire body
            text = soup.get_text(separator=' ', strip=True)
        
        # Clean up text
        text = self._clean_text(text)
        
        return text
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing extra whitespace and special characters.
        
        Args:
            text: Raw text
        
        Returns:
            Cleaned text
        """
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text