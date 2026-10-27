# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

# SEO Prism — Backend

FastAPI application, async crawler and analysis pipeline, CLI and MCP server.
The web panel lives in [`frontend/`](../frontend) and can be served by this
same API process (see `SEO_PRISM_STATIC_DIR` below).

## Installation

Requires Python 3.10+ (CI and the Docker image use 3.12).

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

### API

```bash
python -m api.main
```

Serves `http://localhost:8000` with `GET /`, `POST /scan`,
`GET /scans`, `GET /results`, `GET /results/{scan_id}` and `GET /health`.
Scan history is stored in a SQLite file (`scans.db`, created relative to the
working directory); timestamps are written in UTC with an explicit offset and
legacy naive rows are converted on read.

Issue totals report actionable issues only. Info-level entries (robots.txt,
sitemap, security.txt and llms.txt found) remain in the issue list so their
section can show them, but are excluded from `total_issues`, from the history
and CLI counters and from `seo_grade.breakdown.total`; `POST /scan`, the CLI
summary and `GET /results/{scan_id}` expose them as `info_notices`. The
accounting lives in `core/issues.py`.

Page analysis (BeautifulSoup plus the modules that read it) runs in a worker
thread via `asyncio.to_thread`, so `/health` and other requests keep answering
while a scan is in progress.

### CLI

```bash
python cli.py --url https://example.com
python cli.py --url https://example.com --json > scan_results.json
```

All options (`--max-pages`, `--generate-report`, `--lang`, ...): run
`python cli.py --help` or see the [root README](../README.md).

### MCP server

```bash
python mcp_server.py                  # stdio transport (what agents launch)
python mcp_server.py --transport streamable-http --port 8080
```

One tool, `seo_scan(url, max_pages)`, returning the same payload as
`cli.py --json`. Client configurations for Hermes Agent, Claude Code, Codex,
Devin and OpenClaw are in the [root README](../README.md#mcp-server-ai-agents).

## Docker quickstart

From the repository root:

```bash
docker compose up --build
```

Then open <http://localhost:8000>: the API serves the compiled web panel from
`/app/static` (the API-info endpoint keeps precedence at `/`, so the panel
itself is at `/index.html`) and stores scan history in `/app/scans.db` inside
the container. To keep the database across container recreation, create the
file on the host and uncomment the `volumes` block in
[`docker-compose.yml`](../docker-compose.yml):

```bash
touch scans.db
docker compose up --build
```

The panel is built with the API origin `http://localhost:8000` baked in. If
you reach the container from another host, rebuild with:

```bash
docker compose build --build-arg VITE_API_BASE_URL=https://seo.example.com
```

## Environment variables

All of them are optional; unset means the documented default.

| Variable | Default | Description |
|---|---|---|
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated origins accepted by the API's CORS middleware. Only needed when the panel is served from a different origin than the API (the Vite dev server, or a separately hosted panel). |
| `SEO_PRISM_MAX_PAGES_LIMIT` | unset — **no cap** | Operator guard: upper bound on the `max_pages` requested per scan. The open-source edition ships with no ceiling; set this (e.g. `100`) only when you host the tool for other people and want to bound crawl size and resource usage. An invalid or non-positive value is ignored with a logged warning rather than breaking scans. |
| `SEO_PRISM_API_KEY` | unset — API open | Operator guard: when set, every endpoint except `/health` requires the key in an `X-API-Key` request header; a missing or wrong key gets `401`. Use it when the instance is reachable beyond your machine. The bundled panel reacts to a `401` by opening an API-key field stored in `sessionStorage` and sends the key with every request; it is never included in the build. The Docker healthcheck uses `/health` and therefore stays healthy with the key enabled. |
| `SEO_PRISM_BLOCK_PRIVATE_TARGETS` | unset — disabled | Operator guard for public deployments: set it to `1` to reject any host resolving to a loopback, private, link-local, CGNAT or reserved address (including `169.254.169.254`). The aiohttp connector validates the scan target and every redirect, external resource, robots.txt and StandardFiles request, including IP literals, so the crawler cannot be used as an SSRF pivot against your internal network. It validates at connect time without pinning a separate DNS resolution (residual DNS-rebinding risk). The HTTP API, MCP server and CLI all honour it. Leave it unset for local development, where scanning `localhost` is the intended use. |
| `SEO_PRISM_STATIC_DIR` | unset — API only | Directory containing the compiled frontend (`frontend/dist`). When set to an existing directory, the API serves it at `/` while keeping every API route reachable, so a single process hosts panel and API. The Docker image sets it to `/app/static`. |

Example for a public deployment (set only what you need):

```bash
SEO_PRISM_API_KEY=change-me \
SEO_PRISM_BLOCK_PRIVATE_TARGETS=1 \
SEO_PRISM_MAX_PAGES_LIMIT=100 \
python -m api.main
```

## Tests

```bash
cd backend
venv/bin/pytest
```

The suite must be launched from `backend/`: `pytest.ini` defines the rootdir
there and `tests/conftest.py` puts `backend/` on `sys.path` for the flat
imports (`core.*`, `modules.*`, `database`, ...).
