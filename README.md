# SEO Prism

SEO Analyzer Tool - Detect broken links and missing meta-tags

## Features

- ✅ Accepts any URL (localhost, production, custom ports)
- ✅ Detects broken links and resources (HTTP status ≥ 400)
- ✅ Validates missing meta-tags (`<title>`, `<meta name="description">`)
- ✅ Detects duplicate content (titles, descriptions and H1 headers)
- ✅ Analyzes H1 headers (missing, multiple, duplicate)
- ✅ Validates header hierarchy (proper H1-H6 structure)
- ✅ Checks image alt text (missing, short alt tags)
- ✅ Validates standard files: robots.txt, security.txt (both locations), llms.txt and sitemaps (14 documented name scenarios including Astro `sitemap-index.xml`, WordPress `wp-sitemap.xml` and `.well-known/sitemap.xml`, plus the `Sitemap:` directive in robots.txt)
- ✅ Analyzes meta robots directives (noindex, nofollow, nosnippet, etc.)
- ✅ Validates canonical tags (missing, empty, chains, 404s, redirects, URL variations)
- ✅ Validates hreflang tags (invalid/duplicate codes, missing return links, x-default)
- ✅ Analyzes structured data (JSON-LD, Microdata, RDFa)
- ✅ Detects orphan pages and thin content; validates title/meta description lengths
- ✅ Fair SEO grading (A-F) with a logarithmic error-density scale: same error density gives the same score regardless of site size
- ✅ Premium prism-themed web panel (dark crystal UI, Tailwind CSS v4)
- ✅ Bilingual UI (EN/ES): the web panel auto-detects the browser language (Spanish for `es-*`, English otherwise)
- ✅ CLI with full untruncated output and `--json` mode for AI agents
- ✅ MCP server (`seo_scan` tool) + agent skill for AI agents (Hermes Agent, Claude Code, Codex, Devin, OpenClaw)
- ✅ Executive SEO report in PDF (Spanish/English, zero truncation, print-ready)
- ✅ Local mode (ignores robots.txt)

## SEO Grading

Each issue is weighted by severity (high ×3, medium ×1, low ×0.5) and divided by the number of
crawled pages to get the error density `d`. The score uses a logarithmic penalty
(`100 · (1 − log10(1+d) / log10(1+10))`), so a small site with many errors always scores worse
than a large site with fewer, two sites with the same error density get exactly the same score,
and the scale keeps discriminating beyond the point where a linear one would collapse to F.
The letter (A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60, F below) is derived from the rounded score.

## Installation

### Backend (Python)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend (React)

```bash
cd frontend
pnpm install
cp .env.example .env
```

## Usage

### Start Backend API

```bash
cd backend
source venv/bin/activate
python -m api.main
```

API will be available at `http://localhost:8000`

Set `CORS_ORIGINS` (comma-separated) to allow other frontend origins —
defaults to `http://localhost:5173`:

```bash
CORS_ORIGINS=https://app.example.com python -m api.main
```

### Start Frontend

```bash
cd frontend
pnpm dev
```

Frontend will be available at `http://localhost:5173`

### CLI Usage

```bash
cd backend
source venv/bin/activate
python cli.py --url http://localhost:3000
python cli.py --url https://example.com --max-pages 50
```

### JSON Output (`--json`)

Add `--json` to get the complete analysis in a single machine-readable document (ideal for AI agents or piping to `jq`). Progress messages go to `stderr` and `stdout` contains ONLY the JSON payload with the keys `scan`, `issues` (every issue, untruncated), `seo_grade` and `resource_analysis`; page HTML is excluded to keep the output compact.

```bash
python cli.py --url https://example.com --json > scan_results.json
python cli.py --url https://example.com --json 2>/dev/null | jq '.issues | length'
```

### Generate Professional SEO Report

Generate a professional executive SEO report. The default format is **PDF** (complete, print-ready, every issue listed with automatic pagination — no manual adjustments needed). Reports are fully bilingual (`--lang es|en`): category labels, issue descriptions and section texts are all translated. The legacy PowerPoint format is still available as an editable option.

```bash
cd backend
source venv/bin/activate
python cli.py --url <URL> --generate-report                       # PDF (default)
python cli.py --url <URL> --generate-report --report-format pptx  # editable PowerPoint
```

**Available options:**
- `--url` (required): Target URL to scan
- `--max-pages` (optional, default 100): Maximum number of pages to crawl
- `--json` (flag): Print complete scan results as JSON to stdout (progress goes to stderr)
- `--generate-report` (flag): Enable report generation
- `--report-format` (optional, default `pdf`): `pdf` or `pptx`
- `--lang` (optional, default 'en'): Report language - 'es' for Spanish, 'en' for English
- `--output` (optional): Output file path (default: `seo_report.pdf` or `seo_report.pptx` per format)

**Examples:**
```bash
# Generate PDF report in Spanish
python cli.py --url https://example.com --generate-report --lang es --output reporte_seo.pdf

# Generate report in English (default PDF)
python cli.py --url https://example.com --generate-report

# Editable PowerPoint version
python cli.py --url https://example.com --generate-report --report-format pptx

# With page limit and Spanish report
python cli.py --url http://localhost:3000 --max-pages 50 --generate-report --lang es
```

## MCP Server (AI Agents)

`backend/mcp_server.py` wraps the scan pipeline as a [Model Context Protocol](https://modelcontextprotocol.io) server. It exposes one tool, `seo_scan(url, max_pages)`, returning `{scan, issues, seo_grade, resource_analysis}` — the same payload as `cli.py --json`.

```bash
cd backend
source venv/bin/activate      # or: pip install -r requirements.txt
python mcp_server.py          # stdio transport (what agents launch)

# Optional HTTP transport for remote clients:
python mcp_server.py --transport streamable-http --port 8080
```

Register the server in your agent, replacing `/path/to/seo-prism/backend` with the real path (use the venv python so dependencies resolve):

**Hermes Agent** — `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  seo-prism:
    command: "/path/to/seo-prism/backend/venv/bin/python"
    args: ["/path/to/seo-prism/backend/mcp_server.py"]
    cwd: "/path/to/seo-prism/backend"
```

**Claude Code** — from the repo root:

```bash
claude mcp add seo-prism -- /path/to/seo-prism/backend/venv/bin/python /path/to/seo-prism/backend/mcp_server.py
```

**Codex** — `~/.codex/config.toml`:

```toml
[mcp_servers.seo-prism]
command = "/path/to/seo-prism/backend/venv/bin/python"
args = ["/path/to/seo-prism/backend/mcp_server.py"]
```

**Devin** — Settings → MCP servers → custom server, STDIO transport, same command/args as above.

**OpenClaw** — config (`mcp.servers`) or `openclaw mcp add`:

```json5
{
  mcp: {
    servers: {
      seo-prism: {
        command: "/path/to/seo-prism/backend/venv/bin/python",
        args: ["/path/to/seo-prism/backend/mcp_server.py"],
      },
    },
  },
}
```

Agents that can run shells don't need MCP: `cli.py --json` works directly — see `skills/seo-prism/SKILL.md` for a ready-made agent skill.

## API Endpoints

- `GET /` - API info
- `POST /scan` - Start a new scan
- `GET /results` - Get latest scan results
- `GET /results/{scan_id}` - Get specific scan results

## Testing

The backend pytest suite covers every analysis module, the CLI, both report
generators, the grading fairness guarantees and the standard-file discovery scenarios
(integration tests with a real HTTP server).

```bash
cd backend
venv/bin/pytest
```

## Project Structure

```
seo-prism/
├── backend/
│   ├── core/
│   │   ├── crawler.py
│   │   ├── pipeline.py
│   │   ├── soup.py
│   │   └── url_utils.py
│   ├── modules/
│   │   ├── broken_links.py
│   │   ├── canonical_tags.py
│   │   ├── duplicate_content.py
│   │   ├── header_hierarchy.py
│   │   ├── hreflang.py
│   │   ├── image_alt_text.py
│   │   ├── meta_length.py
│   │   ├── meta_robots.py
│   │   ├── meta_tags.py
│   │   ├── orphan_pages.py
│   │   ├── resource_analyzer.py
│   │   ├── seo_grade.py
│   │   ├── standard_files.py
│   │   ├── structured_data.py
│   │   ├── thin_content.py
│   │   ├── pdf_report_generator.py
│   │   ├── report_generator.py
│   │   ├── report_translations.py
│   │   └── description_translations.py
│   ├── api/
│   │   └── main.py
│   ├── tests/
│   ├── cli.py
│   ├── mcp_server.py
│   ├── database.py
│   ├── version.py
│   ├── requirements.txt
│   └── pyproject.toml
├── skills/
│   └── seo-prism/
│       └── SKILL.md
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── sections/
│   │   │   └── ui/
│   │   ├── hooks/
│   │   │   └── usePagination.ts
│   │   ├── i18n/
│   │   │   ├── en.ts
│   │   │   ├── es.ts
│   │   │   └── index.tsx
│   │   ├── lib/
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── issueMeta.tsx
│   │   ├── filters.ts
│   │   ├── types.ts
│   │   └── version.ts
│   ├── .env.example
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── LICENSE
└── README.md
```

## A small way to support the project

If you are considering the Nous Portal Personal plan, you can use [my Nous Portal referral link](https://portal.nousresearch.com/r/mykeura). It takes **$15 off your first month** and gives me a **$10 referral credit** that helps cover the API usage behind my ongoing work on SEO Prism and related projects. It is entirely optional, but it is a simple way for both of us to benefit.

The offer is for new customers starting a new Personal subscription. It applies to the first invoice, and each payment card can be used for only one referral; if the card has already backed another referral, the discount is reversed and no referral reward is paid.

## License

[AGPL-3.0-only](LICENSE). Every source file carries an `SPDX-License-Identifier`
header. The network-use clause means anyone offering SEO Prism as a hosted
service must publish their modified source — or contact the author for a
commercial license.
