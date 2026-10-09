// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { useState } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faTag } from '@fortawesome/free-solid-svg-icons'
import { Tabs } from '../ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import { getH1Issues, getHeaderHierarchyIssues, getHeaderIssues } from '../../filters'
import { useT } from '../../i18n'
import type { Issue } from '../../types'

type HeaderAnalysisTab = 'all' | 'hierarchy' | 'h1'

export function HeaderAnalysisSection({ issues }: { issues: Issue[] }) {
  const t = useT()
  const [headerAnalysisTab, setHeaderAnalysisTab] = useState<HeaderAnalysisTab>('all')
  const headersPagination = usePagination()
  const hierarchyPagination = usePagination()
  const h1Pagination = usePagination()

  const headerIssues = getHeaderIssues(issues)
  const headerHierarchyIssues = getHeaderHierarchyIssues(issues)
  const h1Issues = getH1Issues(issues)

  const currentIssues =
    headerAnalysisTab === 'all' ? headerIssues :
    headerAnalysisTab === 'hierarchy' ? headerHierarchyIssues :
    h1Issues

  const pagination =
    headerAnalysisTab === 'all' ? headersPagination :
    headerAnalysisTab === 'hierarchy' ? hierarchyPagination :
    h1Pagination

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.sections.headerAnalysis.title}</CardTitle>
        <CardDescription>
          {t.sections.headerAnalysis.description}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs
          ariaLabel={t.sections.headerAnalysis.title}
          tabs={[
            { id: 'all', label: t.sections.headerAnalysis.tabs.all, count: headerIssues.length },
            { id: 'hierarchy', label: t.sections.headerAnalysis.tabs.hierarchy, count: headerHierarchyIssues.length },
            { id: 'h1', label: t.sections.headerAnalysis.tabs.h1, count: h1Issues.length },
          ]}
          active={headerAnalysisTab}
          onChange={setHeaderAnalysisTab}
        />

        {headerIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full border border-success-400/20 bg-success-500/10"><FontAwesomeIcon icon={faTag} className="text-2xl text-success-400" /></div>
            <h3 className="text-xl font-semibold tracking-tight text-success-300 mb-2">{t.sections.headerAnalysis.emptyTitle}</h3>
            <p className="text-muted-foreground">{t.sections.headerAnalysis.emptyBody}</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="space-y-4">
              {currentIssues.slice(0, pagination.visible).map((issue) => (
                <IssueCard key={issue.id} issue={issue} sourceMode="text-if-different" />
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
                {t.sections.headerAnalysis.emptyTab[headerAnalysisTab]}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
