// SPDX-License-Identifier: AGPL-3.0-only
// SPDX-FileCopyrightText: 2026 mykeura <mykeura@hotmail.com>

import { useState } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faFileAlt } from '@fortawesome/free-solid-svg-icons'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import { getMetaDescLengthIssues, getMetaLengthIssues, getTitleLengthIssues } from '../../filters'
import { useT } from '../../i18n'
import type { Issue } from '../../types'

export function MetaLengthSection({ issues }: { issues: Issue[] }) {
  const t = useT()
  const [metaLengthTab, setMetaLengthTab] = useState<'titles' | 'descriptions'>('titles')
  const pagination = usePagination()

  const metaLengthIssues = getMetaLengthIssues(issues)
  const titleLengthIssues = getTitleLengthIssues(metaLengthIssues)
  const metaDescLengthIssues = getMetaDescLengthIssues(metaLengthIssues)
  const currentIssues = metaLengthTab === 'titles' ? titleLengthIssues : metaDescLengthIssues

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.sections.metaLength.title}</CardTitle>
        <CardDescription>
          {t.sections.metaLength.description(metaLengthIssues.length)}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {metaLengthIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full border border-success-400/20 bg-success-500/10"><FontAwesomeIcon icon={faFileAlt} className="text-2xl text-success-400" /></div>
            <h3 className="text-xl font-semibold tracking-tight text-success-300 mb-2">{t.sections.metaLength.emptyTitle}</h3>
            <p className="text-muted-foreground">{t.sections.metaLength.emptyBody}</p>
          </div>
        ) : (
          <>
            <div className="flex gap-2 mb-4 border-b border-border">
              <button
                onClick={() => setMetaLengthTab('titles')}
                className={`px-4 py-2 font-medium transition-colors ${
                  metaLengthTab === 'titles'
                    ? 'text-primary-300 -mb-px border-b-2 border-primary-400 spectrum-underline'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {t.sections.metaLength.tabs.titles} ({titleLengthIssues.length})
              </button>
              <button
                onClick={() => setMetaLengthTab('descriptions')}
                className={`px-4 py-2 font-medium transition-colors ${
                  metaLengthTab === 'descriptions'
                    ? 'text-primary-300 -mb-px border-b-2 border-primary-400 spectrum-underline'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {t.sections.metaLength.tabs.descriptions} ({metaDescLengthIssues.length})
              </button>
            </div>

            <div className="space-y-4">
              {currentIssues.slice(0, pagination.visible).map((issue) => (
                <IssueCard key={issue.id} issue={issue} />
              ))}
              {pagination.hasMore(currentIssues.length) && (
                <div className="text-center mt-4">
                  <ShowMoreButton
                    visible={pagination.visible}
                    total={currentIssues.length}
                    onClick={pagination.loadMore}
                  />
                </div>
              )}
            </div>
            {currentIssues.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                {t.sections.metaLength.emptyTab[metaLengthTab]}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}
