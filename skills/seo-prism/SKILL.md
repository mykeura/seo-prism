---
name: seo-prism
description: Audit a website's SEO (broken links, meta tags, canonical/hreflang, meta robots, structured data, thin content, orphan pages, standard files) and return an A-F grade plus the issue list. Use when asked to check, audit or analyze a site's on-page SEO.
---

# SEO Prism

CLI + MCP interface to the SEO Prism analyzer. Both run the same scan pipeline:
crawl the site, run 12 analysis modules, return structured results.

## Option A — CLI (preferred when you can run a shell)

```bash
cd backend
venv/bin/python cli.py --url https://example.com --max-pages 25 --json
```

- `--json` prints the full payload to stdout; progress goes to stderr.
- `issues[]` entries: `issue_type`, `url`, `source_page`, `description`, `severity`.
- `seo_grade`: `grade` (A-F), `score`, `total_issues`, `severity_counts`.
- Local URLs (localhost, 127.0.0.1, *.test) ignore robots.txt; remote URLs respect it.
- Optional PDF/PPTX report: add `--generate-report --lang en|es`.

## Option B — MCP server (stdio)

Register `backend/mcp_server.py` as an MCP stdio server; it exposes one tool,
`seo_scan(url, max_pages)` returning `{scan, issues, seo_grade, resource_analysis}`.

```bash
python mcp_server.py                     # stdio (agent launches it)
python mcp_server.py --transport streamable-http --port 8080   # remote clients
```

Requires `pip install -r backend/requirements.txt` first.
