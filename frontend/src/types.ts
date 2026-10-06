// SPDX-License-Identifier: AGPL-3.0-only
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

export interface Issue {
  id: number
  issue_type: string
  url: string
  source_page?: string
  description?: string
  severity: string
}

export interface SEOGrade {
  score: number
  grade: string
  breakdown: {
    high: number
    medium: number
    low: number
    total: number
  }
}

export interface ScanResults {
  scan: {
    id: number
    url: string
    timestamp: string
    total_pages: number
    total_issues: number
  }
  issues: Issue[]
  pages: any[]
  seo_grade?: SEOGrade
}

export type SeverityVariant = 'destructive' | 'warning' | 'secondary' | 'outline' | 'default' | 'success'
