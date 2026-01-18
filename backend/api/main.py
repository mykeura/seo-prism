from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.crawler import Crawler
from core.url_utils import is_local, validate_url
from database import Database
from modules.broken_links import BrokenLinksModule
from modules.meta_tags import MetaTagsModule
from modules.meta_robots import MetaRobotsModule
from modules.hreflang import HreflangModule
from modules.standard_files import StandardFilesModule
from modules.duplicate_content import DuplicateContentModule
from modules.image_alt_text import ImageAltTextModule
from modules.canonical_tags import CanonicalTagsModule
from modules.seo_grade import SEOGradeCalculator
from modules.resource_analyzer import ResourceAnalyzer


app = FastAPI(title="SEO Prism API", description="SEO Analyzer Tool API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScanRequest(BaseModel):
    """Request model for scan endpoint."""
    url: str
    max_pages: Optional[int] = 100


class ScanResponse(BaseModel):
    """Response model for scan endpoint."""
    scan_id: int
    url: str
    total_pages: int
    total_issues: int
    message: str
    seo_grade: dict
    resource_analysis: dict


class Issue(BaseModel):
    """Issue model."""
    id: int
    issue_type: str
    url: str
    source_page: Optional[str]
    description: Optional[str]
    severity: str


class ScanResults(BaseModel):
    """Scan results model."""
    scan: dict
    issues: list[Issue]
    pages: list


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SEO Prism API",
        "version": "0.1.0",
        "endpoints": {
            "POST /scan": "Start a new scan",
            "GET /results": "Get latest scan results",
            "GET /results/{scan_id}": "Get specific scan results"
        }
    }


@app.post("/scan", response_model=ScanResponse)
async def start_scan(request: ScanRequest):
    """
    Start a new SEO scan.
    
    Args:
        request: ScanRequest with url and optional max_pages
    
    Returns:
        ScanResponse with scan_id and summary
    """
    # Validate URL
    if not validate_url(request.url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Check if local
    is_local_url = is_local(request.url)
    ignore_robots = is_local_url
    
    try:
        # Initialize database
        db = Database()
        
        # Create scan record
        scan_id = db.create_scan(request.url)
        
        # Crawl website
        async with Crawler(request.url, ignore_robots=ignore_robots) as crawler:
            crawled_pages = await crawler.crawl(max_pages=request.max_pages)
        
        # Store pages in database
        for page in crawled_pages:
            page_id = db.add_page(
                scan_id=scan_id,
                url=page['url'],
                status=page['status'],
                html=page.get('html')
            )
            
            # Store links
            for link in page.get('links', []):
                db.add_link(page_id, link, page['url'])
        
        # Run analysis modules
        broken_links_module = BrokenLinksModule(db)
        meta_tags_module = MetaTagsModule(db)
        meta_robots_module = MetaRobotsModule(db)
        hreflang_module = HreflangModule(db)
        standard_files_module = StandardFilesModule(db)
        duplicate_content_module = DuplicateContentModule(db)
        image_alt_text_module = ImageAltTextModule(db)
        canonical_tags_module = CanonicalTagsModule(db)
        
        broken_link_issues = broken_links_module.analyze(scan_id, crawled_pages)
        meta_tag_issues = meta_tags_module.analyze(scan_id, crawled_pages)
        meta_robots_issues = meta_robots_module.analyze(scan_id, crawled_pages)
        hreflang_issues = hreflang_module.analyze(scan_id, crawled_pages)
        standard_files_issues = await standard_files_module.analyze(scan_id, request.url)
        duplicate_content_issues = duplicate_content_module.analyze(scan_id, crawled_pages)
        image_alt_text_issues = image_alt_text_module.analyze(scan_id, crawled_pages)
        canonical_issues = canonical_tags_module.analyze(scan_id, crawled_pages)
        
        # Update scan totals
        total_issues = len(broken_link_issues) + len(meta_tag_issues) + len(meta_robots_issues) + len(hreflang_issues) + len(standard_files_issues) + len(duplicate_content_issues) + len(image_alt_text_issues) + len(canonical_issues)
        
        # Analyze resources to get actual HTML page count
        resource_analyzer = ResourceAnalyzer()
        resource_analysis = resource_analyzer.analyze_resources(crawled_pages)
        html_page_count = resource_analysis['html_pages']
        
        db.update_scan_totals(scan_id, html_page_count, total_issues)
        
        # Calculate SEO grade
        all_issues = broken_link_issues + meta_tag_issues + meta_robots_issues + hreflang_issues + standard_files_issues + duplicate_content_issues + image_alt_text_issues + canonical_issues
        grade_calculator = SEOGradeCalculator()
        seo_grade = grade_calculator.calculate_grade(html_page_count, all_issues)
        
        db.close()
        
        # Determine message based on local/remote
        if is_local_url:
            message = "Scan completed in fast mode (ignoring robots.txt)"
        else:
            message = "Scan completed"
        
        return ScanResponse(
            scan_id=scan_id,
            url=request.url,
            total_pages=html_page_count,
            total_issues=total_issues,
            message=message,
            seo_grade=seo_grade,
            resource_analysis=resource_analysis
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@app.get("/results", response_model=ScanResults)
async def get_latest_results():
    """
    Get the latest scan results.
    
    Returns:
        ScanResults with scan info, issues, and pages
    """
    try:
        db = Database()
        results = db.get_latest_scan()
        db.close()
        
        if not results:
            raise HTTPException(status_code=404, detail="No scans found")
        
        return ScanResults(
            scan=results['scan'],
            issues=results['issues'],
            pages=results['pages']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")


@app.get("/results/{scan_id}", response_model=ScanResults)
async def get_scan_results(scan_id: int):
    """
    Get specific scan results by ID.
    
    Args:
        scan_id: Scan ID
    
    Returns:
        ScanResults with scan info, issues, and pages
    """
    try:
        db = Database()
        results = db.get_scan_results(scan_id)
        db.close()
        
        if not results or not results.get('scan'):
            raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")
        
        return ScanResults(
            scan=results['scan'],
            issues=results['issues'],
            pages=results['pages']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)