// SPDX-License-Identifier: AGPL-3.0-only
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faFileImage } from '@fortawesome/free-solid-svg-icons'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import { getMissingAltTagIssues } from '../../filters'
import { useT } from '../../i18n'
import type { Issue } from '../../types'

export function ImagesAltSection({ issues }: { issues: Issue[] }) {
  const t = useT()
  const pagination = usePagination()

  const missingAltTagIssues = getMissingAltTagIssues(issues)

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.sections.imagesAlt.title}</CardTitle>
        <CardDescription>
          {t.sections.imagesAlt.description(missingAltTagIssues.length)}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {missingAltTagIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full border border-success-400/20 bg-success-500/10"><FontAwesomeIcon icon={faFileImage} className="text-2xl text-success-400" /></div>
            <h3 className="text-xl font-semibold tracking-tight text-success-300 mb-2">{t.sections.imagesAlt.emptyTitle}</h3>
            <p className="text-muted-foreground">{t.sections.imagesAlt.emptyBody}</p>
          </div>
        ) : (
          <div className="space-y-4">
            {missingAltTagIssues.slice(0, pagination.visible).map((issue) => (
              <IssueCard
                key={issue.id}
                issue={issue}
                urlLabel={t.common.imageUrl}
                sourceMode="link"
                sourceLabel={t.common.foundOnPage}
              />
            ))}
            {pagination.hasMore(missingAltTagIssues.length) && (
              <div className="text-center mt-4">
                <ShowMoreButton
                  visible={pagination.visible}
                  total={missingAltTagIssues.length}
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
