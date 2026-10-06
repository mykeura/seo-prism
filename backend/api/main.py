from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pipeline import run_scan_pipeline
from core.url_utils import is_local, validate_url
from database import Database
from version import __version__


app = FastAPI(title="SEO Prism API", description="SEO Analyzer Tool API", version=__version__)

# Enable CORS for the frontend. Allowlist is configurable via
# CORS_ORIGINS (comma-separated); defaults to the Vite dev origin.
_allowed_origins = [
    origin.strip()
    for origin in os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
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
        "version": __version__,
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
        db = Database()
        pipeline_results = await run_scan_pipeline(
            db, request.url, request.max_pages, ignore_robots
        )
        db.close()
        
        # Determine message based on local/remote
        if is_local_url:
            message = "Scan completed in fast mode (ignoring robots.txt)"
        else:
            message = "Scan completed"
        
        return ScanResponse(
            scan_id=pipeline_results['scan_id'],
            url=request.url,
            total_pages=pipeline_results['html_page_count'],
            total_issues=len(pipeline_results['issues']),
            message=message,
            seo_grade=pipeline_results['seo_grade'],
            resource_analysis=pipeline_results['resource_analysis']
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