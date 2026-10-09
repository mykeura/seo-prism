// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import type { Issue, ScanResults, SEOGrade } from '../types'

let nextId = 1

export function issue(
  issue_type: string,
  severity: string,
  url = 'https://example.com/page',
  extra: Partial<Issue> = {},
): Issue {
  return { id: nextId++, issue_type, severity, url, source_page: url, description: `${issue_type} on ${url}`, ...extra }
}

export function scanResults(issues: Issue[], overrides: Partial<ScanResults['scan']> = {}): ScanResults {
  return {
    scan: {
      id: 7,
      url: 'https://example.com',
      timestamp: '2026-10-08T12:00:00',
      total_pages: 12,
      total_issues: issues.length,
      ...overrides,
    },
    issues,
    pages: [],
  }
}

export const grade = (letter: string, score: number): SEOGrade => ({
  grade: letter,
  score,
  breakdown: { high: 0, medium: 0, low: 0, total: 0 },
})
