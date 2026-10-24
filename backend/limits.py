# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""Shared limits enforced by every entry point (HTTP API, MCP server).

There is no crawl ceiling by default: the open-source tool runs at full
potential. Operators who host the tool for others can set the
SEO_PRISM_MAX_PAGES_LIMIT environment variable to cap max_pages.
"""

import logging
import os
from typing import Optional

_ENV_VAR = "SEO_PRISM_MAX_PAGES_LIMIT"

_logger = logging.getLogger(__name__)


def get_max_pages_limit() -> Optional[int]:
    """Return the configured crawl ceiling, or None when unrestricted.

    A malformed or non-positive value disables the cap (with a logged
    warning) instead of crashing every scan.
    """
    raw = os.environ.get(_ENV_VAR)
    if raw is None or not raw.strip():
        return None
    try:
        limit = int(raw)
    except ValueError:
        _logger.warning("Ignoring %s=%r: value is not an integer", _ENV_VAR, raw)
        return None
    if limit < 1:
        _logger.warning("Ignoring %s=%r: value must be >= 1", _ENV_VAR, raw)
        return None
    return limit


def __getattr__(name: str):
    # Legacy surface for code importing MAX_PAGES_LIMIT directly; it resolves
    # the environment at each access instead of freezing a module constant.
    if name == "MAX_PAGES_LIMIT":
        return get_max_pages_limit()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
