// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faClockRotateLeft, faTriangleExclamation } from '@fortawesome/free-solid-svg-icons'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { cn } from '../lib/utils'
import { useScanHistory } from '../hooks/useScanHistory'
import { getGradeColor } from '../issueMeta'
import { useT } from '../i18n'

interface ScanHistoryProps {
  apiBaseUrl: string
  /** A report is being fetched; rows stay disabled meanwhile. */
  loading: boolean
  /** Bumped by App after a scan finishes so the list picks up the new row. */
  refreshKey: number
  onLoadScan: (scanId: number, grade: { grade: string; score: number }) => void
}

/**
 * History panel: previous scans from GET /scans, one row per scan with its
 * grade, URL, date and issue count. Picking a row reopens that report in App.
 */
export function ScanHistory({ apiBaseUrl, loading, refreshKey, onLoadScan }: ScanHistoryProps) {
  const t = useT()
  const { scans, error, retry } = useScanHistory(apiBaseUrl, refreshKey)

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.history.title}</CardTitle>
        <CardDescription>{t.history.description}</CardDescription>
      </CardHeader>
      <CardContent>
        {error ? (
          <div className="space-y-3">
            <div
              role="alert"
              className="flex items-start gap-3 rounded-xl border border-danger-400/25 bg-danger-500/10 px-4 py-3 text-sm text-danger-200"
            >
              <FontAwesomeIcon icon={faTriangleExclamation} className="mt-0.5 shrink-0 text-danger-300" aria-hidden="true" />
              <span>{error}</span>
            </div>
            <Button variant="outline" size="sm" onClick={retry}>
              {t.history.retry}
            </Button>
          </div>
        ) : scans === null ? (
          <p role="status" className="py-4 text-center text-sm text-muted-foreground">
            {t.history.loading}
          </p>
        ) : scans.length === 0 ? (
          <div className="py-8 text-center">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full border border-white/10 bg-white/[0.03]">
              <FontAwesomeIcon icon={faClockRotateLeft} className="text-2xl text-muted-foreground" />
            </div>
            <h3 className="mb-2 text-xl font-semibold tracking-tight">{t.history.emptyTitle}</h3>
            <p className="text-muted-foreground">{t.history.emptyBody}</p>
          </div>
        ) : (
          <ul className="space-y-2">
            {scans.map((scan) => (
              <li key={scan.scan_id}>
                <button
                  type="button"
                  onClick={() => onLoadScan(scan.scan_id, { grade: scan.grade_letter, score: scan.grade_score })}
                  disabled={loading}
                  className="flex w-full items-center gap-3 rounded-xl border border-white/10 bg-white/[0.03] px-3.5 py-2.5 text-left transition-colors duration-200 hover:border-white/20 hover:bg-white/[0.05] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50"
                >
                  <span
                    className={cn(
                      'inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full border font-display text-sm font-bold',
                      getGradeColor(scan.grade_letter),
                    )}
                  >
                    {scan.grade_letter}
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block truncate font-mono text-[13px] text-primary-300">{scan.url}</span>
                    <span className="mt-0.5 block text-xs text-muted-foreground">
                      {new Date(scan.scan_date).toLocaleString()}
                    </span>
                  </span>
                  <span className="shrink-0 rounded-full bg-white/10 px-2 py-0.5 text-xs font-medium tabular-nums text-foreground">
                    {scan.total_issues}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}
