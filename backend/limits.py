# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""Shared limits enforced by every entry point (HTTP API, MCP server)."""

# Upper bound on pages crawled per scan. Every front door clamps max_pages
# into [1, MAX_PAGES_LIMIT] before calling the pipeline, so no client can
# start an unbounded crawl.
MAX_PAGES_LIMIT = 100
