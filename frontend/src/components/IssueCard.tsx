// SPDX-License-Identifier: AGPL-3.0-only
// SPDX-FileCopyrightText: 2026 mykeura <mykeura@hotmail.com>

import { Badge } from './ui/badge'
import { getIssueIcon, getIssueTypeLabel, getSeverityColor } from '../issueMeta'
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
  return (
    <div
      className={
        tone === 'success'
          ? 'rounded-xl border border-success-400/15 bg-success-500/[0.05] p-4 transition-all duration-200 hover:border-success-400/25 hover:bg-success-500/[0.09]'
          : 'rounded-xl border border-white/10 bg-white/[0.03] p-4 transition-all duration-200 hover:border-white/20 hover:bg-white/[0.06]'
      }
    >
      <div className="flex items-start justify-between gap-4 mb-2">
        <div className="flex items-center gap-2.5">
          <span className="text-xl">{getIssueIcon(issue.issue_type)}</span>
          <span className="font-semibold tracking-tight">{getIssueTypeLabel(issue.issue_type, t.issueTypes)}</span>
        </div>
        <Badge variant={getSeverityColor(issue.severity)}>
          {t.severity[issue.severity] ?? issue.severity.toUpperCase()}
        </Badge>
      </div>
      <div className="space-y-2">
        <div>
          <span className="text-sm text-muted-foreground">{resolvedUrlLabel}</span>
          <a
            href={issue.url}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-2 text-sm text-primary-300 transition-colors break-all hover:text-primary-200 hover:underline"
          >
            {issue.url}
          </a>
        </div>
        {(sourceMode === 'text' && issue.source_page) && (
          <div>
            <span className="text-sm text-muted-foreground">{resolvedSourceLabel}</span>
            <span className="ml-2 text-sm break-all">{issue.source_page}</span>
          </div>
        )}
        {(sourceMode === 'text-if-different' && issue.source_page && issue.source_page !== issue.url) && (
          <div>
            <span className="text-sm text-muted-foreground">{resolvedSourceLabel}</span>
            <span className="ml-2 text-sm break-all">{issue.source_page}</span>
          </div>
        )}
        {(sourceMode === 'link' && issue.source_page) && (
          <div>
            <span className="text-sm text-muted-foreground">{resolvedSourceLabel}</span>
            <a
              href={issue.source_page}
              target="_blank"
              rel="noopener noreferrer"
              className="ml-2 text-sm text-primary-300 transition-colors break-all hover:text-primary-200 hover:underline"
            >
              {issue.source_page}
            </a>
          </div>
        )}
        {issue.description && (
          <div className="text-sm leading-relaxed text-muted-foreground">{issue.description}</div>
        )}
      </div>
    </div>
  )
}
