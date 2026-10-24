# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import hmac
import logging
import sys
import os
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.net_guard import ensure_public_url
from core.pipeline import run_scan_pipeline
from core.url_utils import is_local, validate_url
from database import Database
from limits import get_max_pages_limit
from version import __version__

logger = logging.getLogger(__name__)

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


async def require_api_key(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")
) -> None:
    """Enforce SEO_PRISM_API_KEY when set; a no-op for local open-source use.

    Missing and incorrect keys return the same 401 so the error does not
    reveal which one happened.
    """
    expected = os.environ.get("SEO_PRISM_API_KEY")
    if not expected:
        return
    provided = x_api_key.encode() if x_api_key else b""
    if not hmac.compare_digest(provided, expected.encode()):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "ApiKey"},
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


class ScanHistoryEntry(BaseModel):
    """Single entry of the scan history."""
    scan_id: int
    url: str
    scan_date: str
    grade_letter: str
    grade_score: int
    total_issues: int


class ScanHistoryResponse(BaseModel):
    """Response model for the scan history endpoint."""
    scans: list[ScanHistoryEntry]


def _internal_error() -> HTTPException:
    # Details go to the log only; the response carries a short request id so
    # an operator can correlate it. The id is hex so it is safe to embed.
    ref = uuid.uuid4().hex[:8]
    logger.exception("Request %s failed", ref)
    return HTTPException(status_code=500, detail=f"Internal server error (ref: {ref})")


@app.get("/health")
async def health():
    """Liveness probe for load balancers and container checks (no auth)."""
    return {"status": "ok", "version": __version__}


@app.get("/", dependencies=[Depends(require_api_key)])
async def root():
    """Root endpoint."""
    return {
        "message": "SEO Prism API",
        "version": __version__,
        "endpoints": {
            "POST /scan": "Start a new scan",
            "GET /scans": "List recent scans",
            "GET /results": "Get latest scan results",
            "GET /results/{scan_id}": "Get specific scan results",
            "GET /health": "Health check"
        }
    }


@app.post("/scan", response_model=ScanResponse, dependencies=[Depends(require_api_key)])
async def start_scan(request: ScanRequest):
    """
    Start a new SEO scan.
    
    Args:
        request: ScanRequest with url and optional max_pages
    
    Returns:
        ScanResponse with scan_id and summary
    """
    if not validate_url(request.url):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    # Opt-in SSRF guard for hosted deployments; localhost scanning is a
    # product feature, so the default is off.
    if os.environ.get("SEO_PRISM_BLOCK_PRIVATE_TARGETS") == "1":
        try:
            await ensure_public_url(request.url)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    is_local_url = is_local(request.url)
    ignore_robots = is_local_url
    
    try:
        db = Database()
        # Same clamp the MCP server enforces: max_pages >= 1 always, and an
        # upper bound only when the operator set SEO_PRISM_MAX_PAGES_LIMIT.
        max_pages = request.max_pages if request.max_pages is not None else 100
        max_pages = max(1, max_pages)
        limit = get_max_pages_limit()
        if limit is not None:
            max_pages = min(max_pages, limit)
        pipeline_results = await run_scan_pipeline(
            db, request.url, max_pages, ignore_robots
        )
        db.close()
        
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
    
    except Exception:
        raise _internal_error()


@app.get("/results", response_model=ScanResults, dependencies=[Depends(require_api_key)])
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
    except Exception:
        raise _internal_error()


@app.get("/results/{scan_id}", response_model=ScanResults, dependencies=[Depends(require_api_key)])
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
    except Exception:
        raise _internal_error()


@app.get("/scans", response_model=ScanHistoryResponse, dependencies=[Depends(require_api_key)])
async def list_scans(limit: int = 50):
    """
    List recent scans, newest first.

    Args:
        limit: Maximum entries to return; clamped into [1, 200]

    Returns:
        ScanHistoryResponse with one summary per scan
    """
    limit = max(1, min(limit, 200))
    try:
        db = Database()
        scans = db.list_scans(limit)
        db.close()
        return ScanHistoryResponse(scans=scans)
    except Exception:
        raise _internal_error()


# Static serving for container deployments: mounted last so every API route
# declared above keeps precedence over the frontend bundle.
_static_dir = os.environ.get("SEO_PRISM_STATIC_DIR")
if _static_dir:
    if os.path.isdir(_static_dir):
        app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")
    else:
        logger.warning(
            "SEO_PRISM_STATIC_DIR=%r is not a directory; static serving disabled",
            _static_dir,
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
