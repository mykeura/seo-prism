# SEO Prism

SEO Analyzer Tool - Detect broken links and missing meta-tags

## Features

- ✅ Accepts any URL (localhost, production, custom ports)
- ✅ Detects broken links (HTTP status ≥ 400)
- ✅ Validates missing meta-tags (`<title>`, `<meta name="description">`)
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
│   │   └── meta_tags.py
│   ├── api/
│   │   └── main.py
│   ├── cli.py
│   ├── database.py
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UrlInput.tsx
│   │   │   └── ResultsTable.tsx
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
└── README.md
```