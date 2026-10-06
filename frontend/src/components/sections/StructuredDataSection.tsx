// SPDX-License-Identifier: AGPL-3.0-only
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faDatabase } from '@fortawesome/free-solid-svg-icons'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import { getStructuredDataIssues } from '../../filters'
import { useT } from '../../i18n'
import type { Issue } from '../../types'

export function StructuredDataSection({ issues }: { issues: Issue[] }) {
  const t = useT()
  const pagination = usePagination()

  const structuredDataIssues = getStructuredDataIssues(issues)

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.sections.structuredData.title}</CardTitle>
        <CardDescription>
          {t.sections.structuredData.description(structuredDataIssues.length)}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {structuredDataIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full border border-success-400/20 bg-success-500/10"><FontAwesomeIcon icon={faDatabase} className="text-2xl text-success-400" /></div>
            <h3 className="text-xl font-semibold tracking-tight text-success-300 mb-2">{t.sections.structuredData.emptyTitle}</h3>
            <p className="text-muted-foreground">{t.sections.structuredData.emptyBody}</p>
          </div>
        ) : (
          <div className="space-y-4">
            {structuredDataIssues.slice(0, pagination.visible).map((issue) => (
              <IssueCard key={issue.id} issue={issue} />
            ))}
            {pagination.hasMore(structuredDataIssues.length) && (
              <div className="text-center mt-4">
                <ShowMoreButton
                  visible={pagination.visible}
                  total={structuredDataIssues.length}
                  label={t.sections.structuredData.showMoreLabel}
                  onClick={pagination.loadMore}
                />
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
