// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

/** One entry of GET /scans: a finished scan with its stored summary. */
export interface ScanHistoryEntry {
  scan_id: number
  url: string
  scan_date: string
  grade_letter: string
  grade_score: number
  total_issues: number
}

/** Response body of GET /scans. */
export interface ScansResponse {
  scans: ScanHistoryEntry[]
}
