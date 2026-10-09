// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { Badge } from './ui/badge'
import { cn } from '../lib/utils'
import {
  getIssueIcon,
  getIssueTypeLabel,
  getSeverityColor,
  isSeverity,
  severityFill,
} from '../issueMeta'
import { useT } from '../i18n'
import type { Issue } from '../types'

type IssueCardTone = 'default' | 'success'
type SourceMode = 'none' | 'text' | 'text-if-different' | 'link'

interface IssueCardProps {
  issue: Issue
  tone?: IssueCardTone
  urlLabel?: string
  sourceMode?: SourceMode
  sourceLabel?: string
}

const linkClass =
  'font-mono text-[13px] text-primary-300 transition-colors break-all hover:text-primary-200 hover:underline'

export function IssueCard({
  issue,
  tone = 'default',
  urlLabel,
  sourceMode = 'none',
  sourceLabel,
}: IssueCardProps) {
  const t = useT()
  const resolvedUrlLabel = urlLabel ?? t.common.url
  const resolvedSourceLabel = sourceLabel ?? t.common.source
  const accent =
    tone === 'success'
      ? 'bg-success-400'
      : isSeverity(issue.severity)
        ? severityFill[issue.severity]
        : 'bg-white/20'

  const showSource =
    issue.source_page &&
    (sourceMode === 'text' ||
      sourceMode === 'link' ||
      (sourceMode === 'text-if-different' && issue.source_page !== issue.url))

  return (
    <div
      className={cn(
        'relative overflow-hidden rounded-xl border py-3.5 pl-5 pr-4 transition-colors duration-200',
        tone === 'success'
          ? 'border-success-400/15 bg-success-500/[0.05] hover:border-success-400/25 hover:bg-success-500/[0.08]'
          : 'border-white/10 bg-white/[0.03] hover:border-white/20 hover:bg-white/[0.05]',
      )}
    >
      <span aria-hidden="true" className={cn('absolute inset-y-0 left-0 w-[3px]', accent)} />

      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2.5">
          <span className="shrink-0 text-base">{getIssueIcon(issue.issue_type)}</span>
          <span className="font-medium tracking-tight">
            {getIssueTypeLabel(issue.issue_type, t.issueTypes)}
          </span>
        </div>
        <Badge variant={getSeverityColor(issue.severity)}>
          {t.severity[issue.severity] ?? issue.severity}
        </Badge>
      </div>

      <dl className="mt-2.5 space-y-1.5 text-sm">
        <div className="flex gap-2">
          <dt className="shrink-0 text-muted-foreground">{resolvedUrlLabel}</dt>
          <dd className="min-w-0">
            <a href={issue.url} target="_blank" rel="noopener noreferrer" className={linkClass}>
              {issue.url}
            </a>
          </dd>
        </div>
        {showSource && (
          <div className="flex gap-2">
            <dt className="shrink-0 text-muted-foreground">{resolvedSourceLabel}</dt>
            <dd className="min-w-0">
              {sourceMode === 'link' ? (
                <a
                  href={issue.source_page}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={linkClass}
                >
                  {issue.source_page}
                </a>
              ) : (
                <span className="font-mono text-[13px] break-all">{issue.source_page}</span>
              )}
            </dd>
          </div>
        )}
      </dl>

      {issue.description && (
        <p className="mt-2.5 text-sm leading-relaxed text-muted-foreground">
          {issue.description}
        </p>
      )}
    </div>
  )
}
