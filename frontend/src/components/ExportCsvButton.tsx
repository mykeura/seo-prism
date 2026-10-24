// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faFileCsv } from '@fortawesome/free-solid-svg-icons'
import { Button } from './ui/button'
import { useT } from '../i18n'
import type { Issue } from '../types'

function csvField(value: string | undefined): string {
  return `"${(value ?? '').replace(/"/g, '""')}"`
}

/** Every field quoted and inner quotes doubled, so commas and newlines survive. */
export function issuesToCsv(issues: Issue[]): string {
  const header = ['issue_type', 'url', 'source_page', 'severity', 'description']
  const rows = issues.map((issue) =>
    [issue.issue_type, issue.url, issue.source_page, issue.severity, issue.description]
      .map(csvField)
      .join(','),
  )
  return [header.map(csvField).join(','), ...rows].join('\n')
}

interface ExportCsvButtonProps {
  issues: Issue[]
  filename: string
}

/** Downloads the section's issues as a CSV built entirely client-side. */
export function ExportCsvButton({ issues, filename }: ExportCsvButtonProps) {
  const t = useT()

  const download = () => {
    const blob = new Blob([issuesToCsv(issues)], { type: 'text/csv;charset=utf-8' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.click()
    URL.revokeObjectURL(link.href)
  }

  return (
    <Button variant="ghost" size="sm" onClick={download} disabled={issues.length === 0}>
      <FontAwesomeIcon icon={faFileCsv} aria-hidden="true" />
      {t.csvExport.button}
    </Button>
  )
}
