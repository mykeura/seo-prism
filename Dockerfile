# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

# ---- Stage 1: build the web panel ----
FROM node:26-slim AS frontend-build

# corepack is no longer bundled with Node >= 25; install pnpm directly.
# Version pinned to match frontend/pnpm-lock.yaml (lockfileVersion 9.0).
RUN npm install -g pnpm@12.15.0

# API origin baked into the bundle. Empty falls back to http://localhost:8000
# in the app code; rebuild with --build-arg VITE_API_BASE_URL=https://seo.example.com
# when the panel is reached from another host.
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

WORKDIR /build
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
COPY frontend/tsconfig.json frontend/tsconfig.node.json frontend/vite.config.ts frontend/index.html ./
COPY frontend/src/ src/
COPY frontend/public/ public/
RUN pnpm install --frozen-lockfile && pnpm build

# ---- Stage 2: API server + compiled panel ----
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime code only: venv, tests and build metadata stay out of the image.
COPY backend/api/ api/
COPY backend/core/ core/
COPY backend/modules/ modules/
COPY backend/cli.py backend/database.py backend/limits.py backend/mcp_server.py backend/version.py ./

# Compiled panel, served by the API through SEO_PRISM_STATIC_DIR.
COPY --from=frontend-build /build/dist/ static/
ENV SEO_PRISM_STATIC_DIR=/app/static

# SQLite scans.db is created relative to the working directory.
RUN useradd --system --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5)"]
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
