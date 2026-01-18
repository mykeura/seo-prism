from typing import List, Dict
from bs4 import BeautifulSoup
import json
from database import Database


class StructuredDataModule:
    """Module to validate Schema/Structured Data (JSON-LD, Microdata, RDFa)."""
    
    # Common Schema.org types
    SCHEMA_TYPES = {
        'WebPage', 'WebSite', 'Article', 'BlogPosting', 'NewsArticle', 'TechArticle',
        'Organization', 'Person', 'LocalBusiness', 'Restaurant', 'Hotel',
        'Product', 'Offer', 'Review', 'AggregateRating', 'Rating',
        'BreadcrumbList', 'ListItem', 'FAQPage', 'Question', 'Answer',
        'HowTo', 'Recipe', 'Event', 'JobPosting', 'VideoObject', 'ImageObject',
        'Book', 'Movie', 'MusicRecording', 'CreativeWork',
        'SearchAction', 'EntryPoint', 'Action'
    }
    
    # Required properties by schema type
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
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Analyze JSON-LD
            json_ld_issues = self._analyze_json_ld(soup, page_url)
            issues.extend(json_ld_issues)
            
            # Analyze Microdata
            microdata_issues = self._analyze_microdata(soup, page_url)
            issues.extend(microdata_issues)
            
            # Analyze RDFa
            rdfa_issues = self._analyze_rdfa(soup, page_url)
            issues.extend(rdfa_issues)
        
        # Add all issues to database
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
        
        # Find all JSON-LD scripts
        json_ld_scripts = soup.find_all('script', attrs={'type': 'application/ld+json'})
        
        if not json_ld_scripts:
            # No JSON-LD found - this is a warning, not an error
            issue = {
                'issue_type': 'missing_json_ld',
                'url': page_url,
                'source_page': page_url,
                'description': 'No JSON-LD structured data found',
                'severity': 'low'
            }
            issues.append(issue)
            return issues
        
        # Validate each JSON-LD script
        for script in json_ld_scripts:
            try:
                # Parse JSON
                data = json.loads(script.string)
                
                # Handle @graph structure or single object
                if '@graph' in data:
                    # Extract top-level schemas from @graph
                    schemas = data['@graph']
                elif isinstance(data, list):
                    # Array of schemas
                    schemas = data
                else:
                    # Single schema object
                    schemas = [data]
                
                # Validate each top-level schema
                for schema in schemas:
                    self._validate_schema(schema, page_url, issues)
            
            except json.JSONDecodeError as e:
                issues.append({
                    'issue_type': 'json_ld_invalid_json',
                    'url': page_url,
                    'source_page': page_url,
                    'description': f'Invalid JSON-LD syntax: {str(e)}',
                    'severity': 'high'
                })
        
        return issues
    
    def _validate_schema(self, schema: Dict, page_url: str, issues: List[Dict]):
        """
        Validate a single schema object (recursively validates nested schemas).
        
        Args:
            schema: Schema object to validate
            page_url: Page URL
            issues: List to append issues to
        """
        schema_type = schema.get('@type')
        
        if not schema_type:
            # Only report missing @type for top-level schemas
            # Nested schemas without @type are often valid (e.g., plain objects)
            if '@context' in schema or '@id' in schema:
                issues.append({
                    'issue_type': 'json_ld_missing_type',
                    'url': page_url,
                    'source_page': page_url,
                    'description': 'JSON-LD schema missing @type property',
                    'severity': 'high'
                })
            return
        
        # Check if schema type is recognized
        if schema_type not in self.SCHEMA_TYPES:
            issues.append({
                'issue_type': 'json_ld_unknown_type',
                'url': page_url,
                'source_page': page_url,
                'description': f'Unknown schema type: {schema_type}',
                'severity': 'medium'
            })
            return
        
        # Check for required properties
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
        
        # Validate specific properties
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
        
        # Find all elements with itemscope
        microdata_elements = soup.find_all(attrs={'itemscope': True})
        
        if not microdata_elements:
            # No Microdata found
            issue = {
                'issue_type': 'missing_microdata',
                'url': page_url,
                'source_page': page_url,
                'description': 'No Microdata structured data found',
                'severity': 'low'
            }
            issues.append(issue)
            return issues
        
        # Validate each microdata element
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
            
            # Extract schema type from URL
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
        
        # Find all elements with typeof
        rdfa_elements = soup.find_all(attrs={'typeof': True})
        
        if not rdfa_elements:
            # No RDFa found
            issue = {
                'issue_type': 'missing_rdfa',
                'url': page_url,
                'source_page': page_url,
                'description': 'No RDFa structured data found',
                'severity': 'low'
            }
            issues.append(issue)
            return issues
        
        # Validate each RDFa element
        for element in rdfa_elements:
            typeof_value = element.get('typeof')
            
            if not typeof_value:
                continue
            
            # Extract schema type
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