# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""MCP server exposing the SEO Prism scan pipeline to AI agents.

Usage:
    python mcp_server.py                          # stdio (default, for MCP clients)
    python mcp_server.py --transport streamable-http --port 8080
"""

import argparse
import sys
from typing import Any, Callable

from mcp.server.fastmcp import FastMCP

from core.pipeline import run_scan_pipeline
from core.url_utils import is_local, validate_url
from database import Database
from version import __version__

MAX_PAGES_LIMIT = 100

# FastMCP pins the HTTP host/port on the instance (run() only takes the
# transport), so the CLI defaults live here.
_DEFAULT_HOST = "127.0.0.1"
_DEFAULT_PORT = 8080


def build_server(
    host: str = _DEFAULT_HOST, port: int = _DEFAULT_PORT
) -> tuple[FastMCP, Callable[..., Any]]:
    server = FastMCP(
        name="seo-prism",
        instructions=(
            "SEO audit tool: call seo_scan with a public URL and it returns the "
            "crawled issues, the SEO grade and the resource analysis. Issues are "
            "English-only; fields are issue_type, url, source_page, description, severity."
        ),
        host=host,
        port=port,
    )
    # FastMCP drops the project version (it reports the MCP SDK version by
    # default). Propagate ours to the low-level server so clients see 1.23.0.
    server._mcp_server.version = __version__

    @server.tool(
        name="seo_scan",
        description=(
            "Run a full SEO audit on a website: crawls the site and reports broken "
            "links/resources, meta tag issues, header hierarchy, canonical/hreflang, "
            "meta robots, structured data, thin content, orphan pages and standard "
            "files (robots.txt, sitemap, security.txt, llms.txt). Returns the issue "
            "list, the A-F SEO grade and a resource analysis summary."
        ),
    )
    async def seo_scan(url: str, max_pages: int = 25) -> dict:
        if not validate_url(url):
            return {"error": f"Invalid URL: {url}"}

        max_pages = max(1, min(max_pages, MAX_PAGES_LIMIT))
        db = Database()
        try:
            result = await run_scan_pipeline(
                db, url, max_pages, ignore_robots=is_local(url)
            )
        finally:
            db.close()

        return {
            "scan": {
                "id": result["scan_id"],
                "url": url,
                "pages_analyzed": result["html_page_count"],
                "total_issues": len(result["issues"]),
                "version": __version__,
            },
            "issues": result["issues"],
            "seo_grade": result["seo_grade"],
            "resource_analysis": result["resource_analysis"],
        }

    return server, seo_scan


# Module-level handle so the tool can be called directly (programmatic use and
# tests) without going through the MCP transport.
server, seo_scan = build_server()


def main() -> None:
    parser = argparse.ArgumentParser(description="SEO Prism MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="MCP transport (default: stdio)",
    )
    parser.add_argument("--host", default=_DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=_DEFAULT_PORT)
    args = parser.parse_args()

    server, _seo_scan = build_server(host=args.host, port=args.port)

    if args.transport == "streamable-http":
        server.run(transport="streamable-http")
    else:
        server.run(transport="stdio")


if __name__ == "__main__":
    sys.exit(main())
