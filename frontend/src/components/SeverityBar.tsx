// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { cn } from '../lib/utils'
import { SEVERITY_ORDER, severityFill, type Severity } from '../issueMeta'
import { useT } from '../i18n'

export type SeverityCounts = Record<Severity, number>

export function countBySeverity(issues: { severity: string }[]): SeverityCounts {
  const counts: SeverityCounts = { high: 0, medium: 0, low: 0, info: 0 }
  for (const issue of issues) {
    if (issue.severity in counts) counts[issue.severity as Severity] += 1
  }
  return counts
}

/**
 * Issues by severity as a refracted band: each severity takes a slice of the
 * bar in proportion to its count, followed by a legend with the numbers.
 */
export function SeverityBar({ counts }: { counts: SeverityCounts }) {
  const t = useT()
  const present = SEVERITY_ORDER.filter((severity) => counts[severity] > 0)
  const summary = present.map((s) => `${t.severity[s]}: ${counts[s]}`).join(', ')

  return (
    <div>
      <div
        role="img"
        aria-label={`${t.overview.severityBarLabel}. ${summary}`}
        className="flex h-2.5 w-full gap-0.5 overflow-hidden rounded-full bg-white/[0.06]"
      >
        {present.map((severity) => (
          <span
            key={severity}
            data-severity={severity}
            className={cn('h-full min-w-1 first:rounded-l-full last:rounded-r-full', severityFill[severity])}
            style={{ flexGrow: counts[severity], flexBasis: 0 }}
          />
        ))}
      </div>
      <ul className="mt-3 flex flex-wrap gap-x-5 gap-y-1.5 text-sm">
        {SEVERITY_ORDER.map((severity) => (
          <li
            key={severity}
            className={cn(
              'flex items-center gap-2',
              counts[severity] === 0 && 'opacity-45',
            )}
          >
            <span aria-hidden="true" className={cn('h-2 w-2 rounded-full', severityFill[severity])} />
            <span className="text-muted-foreground">{t.severity[severity]}</span>
            <span className="font-medium tabular-nums">{counts[severity]}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
