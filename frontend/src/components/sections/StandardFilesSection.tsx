// SPDX-License-Identifier: AGPL-3.0-only
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faFolder } from '@fortawesome/free-solid-svg-icons'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import { getStandardFilesIssues } from '../../filters'
import { useT } from '../../i18n'
import type { Issue } from '../../types'

export function StandardFilesSection({ issues }: { issues: Issue[] }) {
  const t = useT()
  const pagination = usePagination()

  const standardFilesIssues = getStandardFilesIssues(issues)

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.sections.standardFiles.title}</CardTitle>
        <CardDescription>
          {t.sections.standardFiles.description(standardFilesIssues.length)}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {standardFilesIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full border border-white/10 bg-white/[0.04]"><FontAwesomeIcon icon={faFolder} className="text-2xl text-primary-300" /></div>
            <h3 className="text-xl font-semibold tracking-tight text-muted-foreground mb-2">{t.sections.standardFiles.emptyTitle}</h3>
            <p className="text-muted-foreground">{t.sections.standardFiles.emptyBody}</p>
          </div>
        ) : (
          <div className="space-y-4">
            {standardFilesIssues.slice(0, pagination.visible).map((issue) => (
              <IssueCard key={issue.id} issue={issue} tone="success" />
            ))}
            {pagination.hasMore(standardFilesIssues.length) && (
              <div className="text-center mt-4">
                <ShowMoreButton
                  visible={pagination.visible}
                  total={standardFilesIssues.length}
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
