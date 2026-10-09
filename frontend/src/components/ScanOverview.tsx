// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { Card } from './ui/card'
import { GradeGauge } from './GradeGauge'
import { SeverityBar, countBySeverity } from './SeverityBar'
import { useT } from '../i18n'
import type { ScanResults, SEOGrade } from '../types'

interface ScanOverviewProps {
  results: ScanResults
  seoGrade: SEOGrade | null
}

export function ScanOverview({ results, seoGrade }: ScanOverviewProps) {
  const t = useT()
  const counts = countBySeverity(results.issues)
  // "found" confirmations (robots.txt present...) travel as info-level
  // items; they are not problems, so they do not count as issues.
  const actionable = counts.high + counts.medium + counts.low
  const description = seoGrade ? t.overview.gradeDescriptions[seoGrade.grade] : undefined

  return (
    <Card>
      <div className="grid gap-8 p-6 sm:p-8 md:grid-cols-[auto_minmax(0,1fr)] md:items-center md:gap-10">
        {seoGrade && (
          <div className="text-center">
            <GradeGauge score={seoGrade.score} grade={seoGrade.grade} />
            <div className="-mt-1 text-sm font-medium">
              <span className="text-muted-foreground">{t.summary.seoGrade}</span>
              {description && <span className="text-foreground">: {description}</span>}
            </div>
          </div>
        )}

        <div className="min-w-0 space-y-6">
          <div className="min-w-0">
            <h2 className="sr-only">{t.overview.title}</h2>
            <a
              href={results.scan.url}
              target="_blank"
              rel="noopener noreferrer"
              title={t.overview.openSite}
              className="block truncate font-mono text-[15px] text-primary-300 transition-colors hover:text-primary-200 hover:underline"
            >
              {results.scan.url}
            </a>
            <p className="mt-1 text-sm text-muted-foreground">
              {t.summary.scanTime}: {new Date(results.scan.timestamp).toLocaleString()}
            </p>
          </div>

          <dl className="grid grid-cols-2 gap-4">
            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
              <dt className="text-sm text-muted-foreground">{t.summary.pagesAnalyzed}</dt>
              <dd className="mt-1 font-display text-4xl font-bold tracking-tight tabular-nums">
                {results.scan.total_pages}
              </dd>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
              <dt className="text-sm text-muted-foreground">{t.overview.issues}</dt>
              <dd
                className={`mt-1 font-display text-4xl font-bold tracking-tight tabular-nums ${
                  actionable === 0 ? 'text-success-300' : 'text-foreground'
                }`}
              >
                {actionable}
              </dd>
            </div>
          </dl>

          <SeverityBar counts={counts} />
        </div>
      </div>
    </Card>
  )
}
