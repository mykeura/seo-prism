from typing import List, Dict
from database import Database


class MissingAltTagsModule:
    """Module to detect images without alt tags for SEO and accessibility."""
    
    def __init__(self, db: Database):
        """
        Initialize the Missing Alt Tags module.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def analyze(self, scan_id: int, crawled_pages: List[Dict]) -> List[Dict]:
        """
        Analyze crawled pages for images without alt tags.
        
        Args:
            scan_id: Scan ID
            crawled_pages: List of crawled page results
        
        Returns:
            List of missing alt tag issues
        """
        issues = []
        
        # Collect all images from all pages
        all_images = []
        for page in crawled_pages:
            page_url = page['url']
            resources = page.get('resources', [])
            
            for resource in resources:
                if resource.get('type') == 'image':
                    all_images.append({
                        'url': resource['url'],
                        'alt': resource.get('alt', ''),
                        'source': page_url
                    })
        
        # Check each image for missing alt tag
        checked_images: set = set()
        for image in all_images:
            image_url = image['url']
            
            # Skip if already checked
            if image_url in checked_images:
                continue
            checked_images.add(image_url)
            
            # Check if alt tag is missing or empty
            alt_text = image.get('alt', '').strip()
            if not alt_text:
                issue = {
                    'issue_type': 'missing_alt_tag',
                    'url': image_url,
                    'source_page': image['source'],
                    'description': 'Image missing alt tag',
                    'severity': 'medium'
                }
                issues.append(issue)
                
                # Add to database
                self.db.add_issue(
                    scan_id=scan_id,
                    issue_type='missing_alt_tag',
                    url=image_url,
                    source_page=image['source'],
                    description='Image missing alt tag',
                    severity='medium'
                )
        
        return issues