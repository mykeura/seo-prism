# SEO Prism

SEO Analyzer Tool - Detect broken links and missing meta-tags

## Features

- ✅ Accepts any URL (localhost, production, custom ports)
- ✅ Detects broken links (HTTP status ≥ 400)
- ✅ Validates missing meta-tags (`<title>`, `<meta name="description">`)
- ✅ Detects duplicate content (titles and descriptions)
- ✅ Analyzes H1 headers (missing, multiple, duplicate)
- ✅ Validates header hierarchy (proper H1-H6 structure)
- ✅ Checks image alt text (missing, short alt tags)
- ✅ Validates standard files (robots.txt, security.txt, sitemap.xml)
- ✅ Analyzes meta robots directives (noindex, nofollow, nosnippet, etc.)
- ✅ Simple web panel without authentication
- ✅ CLI for quick testing
- ✅ Local mode (ignores robots.txt)

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
npm install
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

### Start Frontend

```bash
cd frontend
npm run dev
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

Generate a professional executive SEO report. The default format is **PDF** (complete, print-ready, every issue listed with automatic pagination — no manual adjustments needed). The legacy PowerPoint format is still available as an editable option.

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

## API Endpoints

- `POST /scan` - Start a new scan
- `GET /results` - Get latest scan results
- `GET /results/{scan_id}` - Get specific scan results

## Project Structure

```
seo-prism/
├── backend/
│   ├── core/
│   │   ├── url_utils.py
│   │   └── crawler.py
│   ├── modules/
│   │   ├── broken_links.py
│   │   ├── duplicate_content.py
│   │   ├── h1_analysis.py
│   │   ├── header_hierarchy.py
│   │   ├── image_alt_text.py
│   │   ├── meta_robots.py
│   │   ├── meta_tags.py
│   │   ├── missing_alt_tags.py
│   │   └── standard_files.py
│   ├── api/
│   │   └── main.py
│   ├── cli.py
│   ├── database.py
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ui/
│   │   │       ├── badge.tsx
│   │   │       ├── button.tsx
│   │   │       ├── card.tsx
│   │   │       └── input.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── main.tsx
│   ├── .env.example
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
└── README.md
```