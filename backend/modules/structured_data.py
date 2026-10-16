# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

from typing import List, Dict
from bs4 import BeautifulSoup
import json
from core.soup import soup_for
from database import Database


class StructuredDataModule:
    """Module to validate Schema/Structured Data (JSON-LD, Microdata, RDFa)."""
    
    SCHEMA_TYPES = {
        'WebPage', 'WebSite', 'Article', 'BlogPosting', 'NewsArticle', 'TechArticle',
        'Organization', 'Person', 'LocalBusiness', 'Restaurant', 'Hotel',
        'Product', 'Offer', 'Review', 'AggregateRating', 'Rating',
        'BreadcrumbList', 'ListItem', 'FAQPage', 'Question', 'Answer',
        'HowTo', 'Recipe', 'Event', 'JobPosting', 'VideoObject', 'ImageObject',
        'Book', 'Movie', 'MusicRecording', 'CreativeWork',
        'SearchAction', 'EntryPoint', 'Action'
    }
    
    REQUIRED_PROPERTIES = {
        'Article': ['headline', 'author', 'datePublished', 'publisher'],
        'BlogPosting': ['headline', 'author', 'datePublished', 'publisher'],
        'NewsArticle': ['headline', 'author', 'datePublished', 'publisher'],
        'Organization': ['name', 'url'],
        'Person': ['name'],
        'LocalBusiness': ['name', 'address'],
        'Product': ['name', 'description'],
        'Offer': ['price', 'priceCurrency', 'availability'],
        'Review': ['author', 'reviewRating'],
        'AggregateRating': ['ratingValue', 'reviewCount', 'bestRating', 'worstRating'],
        'BreadcrumbList': ['itemListElement'],
        'FAQPage': ['mainEntity'],
        'HowTo': ['name', 'step'],
        'Recipe': ['name', 'recipeIngredient', 'recipeInstructions'],
        'Event': ['name', 'startDate', 'location']
    }
    
    def __init__(self, db: Database):
        """
        Initialize the Structured Data module.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def analyze(self, scan_id: int, crawled_pages: List[Dict]) -> List[Dict]:
        """
        Analyze crawled pages for structured data issues.
        
        Args:
            scan_id: Scan ID
            crawled_pages: List of crawled page results
        
        Returns:
            List of structured data issues
        """
        issues = []
        
        for page in crawled_pages:
            page_url = page['url']
            html = page.get('html')
            
            if not html:
                continue
            
            soup = soup_for(page)
            
            json_ld_issues = self._analyze_json_ld(soup, page_url)
            json_ld_found = bool(soup.find('script', attrs={'type': 'application/ld+json'}))
            
            microdata_issues = self._analyze_microdata(soup, page_url)
            microdata_found = soup.find(attrs={'itemscope': True})
            
            rdfa_issues = self._analyze_rdfa(soup, page_url)
            rdfa_found = soup.find(attrs={'typeof': True})
            
            if not json_ld_found and not microdata_found and not rdfa_found:
                issues.append({
                    'issue_type': 'missing_structured_data',
                    'url': page_url,
                    'source_page': page_url,
                    'description': 'No structured data found (JSON-LD, Microdata, or RDFa)',
                    'severity': 'medium'
                })
            
            issues.extend(json_ld_issues)
            issues.extend(microdata_issues)
            issues.extend(rdfa_issues)
        
        for issue in issues:
            self.db.add_issue(
                scan_id=scan_id,
                issue_type=issue['issue_type'],
                url=issue['url'],
                source_page=issue['source_page'],
                description=issue['description'],
                severity=issue['severity']
            )
        
        return issues
    
    def _analyze_json_ld(self, soup: BeautifulSoup, page_url: str) -> List[Dict]:
        """
        Analyze JSON-LD structured data.
        
        Args:
            soup: BeautifulSoup object
            page_url: Page URL
        
        Returns:
            List of JSON-LD issues
        """
        issues = []
        
        json_ld_scripts = soup.find_all('script', attrs={'type': 'application/ld+json'})
        
        if not json_ld_scripts:
            return issues
        
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                
                if '@graph' in data:
                    schemas = data['@graph']
                elif isinstance(data, list):
                    schemas = data
                else:
                    schemas = [data]
                
                for schema in schemas:
                    self._validate_schema(schema, page_url, issues, is_top_level=True)
            
            except json.JSONDecodeError as e:
                issues.append({
                    'issue_type': 'json_ld_invalid_json',
                    'url': page_url,
                    'source_page': page_url,
                    'description': f'Invalid JSON-LD syntax: {str(e)}',
                    'severity': 'high'
                })
        
        return issues
    
    def _validate_schema(self, schema: Dict, page_url: str, issues: List[Dict], is_top_level: bool = True):
        """
        Validate a single schema object (recursively validates nested schemas).
        
        Args:
            schema: Schema object to validate
            page_url: Page URL
            issues: List to append issues to
            is_top_level: Whether this is a top-level schema
        """
        schema_type = schema.get('@type')
        
        if not schema_type:
            # Only report missing @type for top-level schemas that should have it
            # Nested schemas without @type are often valid (e.g., mainEntityOfPage, logo)
            if is_top_level and ('@context' in schema or '@id' in schema):
                issues.append({
                    'issue_type': 'json_ld_missing_type',
                    'url': page_url,
                    'source_page': page_url,
                    'description': 'JSON-LD schema missing @type property',
                    'severity': 'high'
                })
            return
        
        if schema_type not in self.SCHEMA_TYPES:
            # Only report unknown type for top-level schemas
            # Nested schemas might have custom types
            if is_top_level:
                issues.append({
                    'issue_type': 'json_ld_unknown_type',
                    'url': page_url,
                    'source_page': page_url,
                    'description': f'Unknown schema type: {schema_type}',
                    'severity': 'medium'
                })
            return
        
        if is_top_level:
            required = self.REQUIRED_PROPERTIES.get(schema_type, [])
            missing = [prop for prop in required if prop not in schema]
            
            if missing:
                issues.append({
                    'issue_type': 'json_ld_missing_properties',
                    'url': page_url,
                    'source_page': page_url,
                    'description': f'Schema {schema_type} missing required properties: {", ".join(missing)}',
                    'severity': 'high'
                })
        
        if schema_type == 'Article' and 'headline' in schema:
            headline = schema['headline']
            if len(headline) < 10:
                issues.append({
                    'issue_type': 'json_ld_short_headline',
                    'url': page_url,
                    'source_page': page_url,
                    'description': f'Article headline too short (< 10 characters): {headline}',
                    'severity': 'medium'
                })
    
    def _analyze_microdata(self, soup: BeautifulSoup, page_url: str) -> List[Dict]:
        """
        Analyze Microdata structured data.
        
        Args:
            soup: BeautifulSoup object
            page_url: Page URL
        
        Returns:
            List of Microdata issues
        """
        issues = []
        
        microdata_elements = soup.find_all(attrs={'itemscope': True})
        
        if not microdata_elements:
            return issues
        
        for element in microdata_elements:
            itemtype = element.get('itemtype')
            
            if not itemtype:
                issues.append({
                    'issue_type': 'microdata_missing_type',
                    'url': page_url,
                    'source_page': page_url,
                    'description': 'Microdata element missing itemtype attribute',
                    'severity': 'high'
                })
                continue
            
            schema_type = itemtype.split('/')[-1]
            
            if schema_type not in self.SCHEMA_TYPES:
                issues.append({
                    'issue_type': 'microdata_unknown_type',
                    'url': page_url,
                    'source_page': page_url,
                    'description': f'Unknown microdata type: {schema_type}',
                    'severity': 'medium'
                })
        
        return issues
    
    def _analyze_rdfa(self, soup: BeautifulSoup, page_url: str) -> List[Dict]:
        """
        Analyze RDFa structured data.
        
        Args:
            soup: BeautifulSoup object
            page_url: Page URL
        
        Returns:
            List of RDFa issues
        """
        issues = []
        
        rdfa_elements = soup.find_all(attrs={'typeof': True})
        
        if not rdfa_elements:
            return issues
        
        for element in rdfa_elements:
            typeof_value = element.get('typeof')
            
            if not typeof_value:
                continue
            
            schema_type = typeof_value.split(':')[-1]
            
            if schema_type not in self.SCHEMA_TYPES:
                issues.append({
                    'issue_type': 'rdfa_unknown_type',
                    'url': page_url,
                    'source_page': page_url,
                    'description': f'Unknown RDFa type: {schema_type}',
                    'severity': 'medium'
                })
        
        return issues