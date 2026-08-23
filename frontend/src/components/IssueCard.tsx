import { Badge } from './ui/badge'
import { getIssueIcon, getIssueTypeLabel, getSeverityColor } from '../issueMeta'
import type { Issue } from '../types'

type IssueCardTone = 'default' | 'emerald'
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
  urlLabel = 'URL:',
  sourceMode = 'none',
  sourceLabel = 'Source:',
}: IssueCardProps) {
  return (
    <div
      className={
        tone === 'emerald'
          ? 'p-4 rounded-lg border border-border bg-emerald-600/5 hover:bg-emerald-600/10 transition-colors'
          : 'p-4 rounded-lg border border-border bg-secondary-600/5 hover:bg-secondary-600/10 transition-colors'
      }
    >
      <div className="flex items-start justify-between gap-4 mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{getIssueIcon(issue.issue_type)}</span>
          <span className="font-semibold">{getIssueTypeLabel(issue.issue_type)}</span>
        </div>
        <Badge variant={getSeverityColor(issue.severity)}>
          {issue.severity.toUpperCase()}
        </Badge>
      </div>
      <div className="space-y-2">
        <div>
          <span className="text-sm text-muted-foreground">{urlLabel}</span>
          <a
            href={issue.url}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-2 text-sm text-primary-400 hover:underline break-all"
          >
            {issue.url}
          </a>
        </div>
        {(sourceMode === 'text' && issue.source_page) && (
          <div>
            <span className="text-sm text-muted-foreground">{sourceLabel}</span>
            <span className="ml-2 text-sm break-all">{issue.source_page}</span>
          </div>
        )}
        {(sourceMode === 'text-if-different' && issue.source_page && issue.source_page !== issue.url) && (
          <div>
            <span className="text-sm text-muted-foreground">{sourceLabel}</span>
            <span className="ml-2 text-sm break-all">{issue.source_page}</span>
          </div>
        )}
        {(sourceMode === 'link' && issue.source_page) && (
          <div>
            <span className="text-sm text-muted-foreground">{sourceLabel}</span>
            <a
              href={issue.source_page}
              target="_blank"
              rel="noopener noreferrer"
              className="ml-2 text-sm text-primary-400 hover:underline break-all"
            >
              {issue.source_page}
            </a>
          </div>
        )}
        {issue.description && (
          <div className="text-sm text-muted-foreground">{issue.description}</div>
        )}
      </div>
    </div>
  )
}
