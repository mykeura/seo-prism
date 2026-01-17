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