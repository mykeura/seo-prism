# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""Issue accounting shared by every output surface.

Info-level entries are confirmations ("robots.txt found", "sitemap found"),
not problems. They stay in the issue list so sections can show them, but
they must not inflate dashboard, history, API, MCP or CLI totals.
"""

from typing import Dict, Iterable


def is_info_notice(issue: Dict) -> bool:
    return str(issue.get('severity') or '').strip().lower() == 'info'


def count_actionable_issues(issues: Iterable[Dict]) -> int:
    return sum(1 for issue in issues if not is_info_notice(issue))
