// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { useState } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faLink } from '@fortawesome/free-solid-svg-icons'
import { Tabs } from '../ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import { getBrokenLinkIssues, getExternalLinks, getInternalLinks } from '../../filters'
import { useT } from '../../i18n'
import type { ScanResults } from '../../types'

export function BrokenLinksSection({ results }: { results: ScanResults }) {
  const t = useT()
  const [activeTab, setActiveTab] = useState<'internal' | 'external'>('internal')
  const pagination = usePagination()

  const brokenLinkIssues = getBrokenLinkIssues(results.issues)
  const internalLinks = getInternalLinks(brokenLinkIssues, results.scan.url)
  const externalLinks = getExternalLinks(brokenLinkIssues, results.scan.url)
  const currentIssues = activeTab === 'internal' ? internalLinks : externalLinks

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.sections.brokenLinks.title}</CardTitle>
        <CardDescription>
          {t.sections.brokenLinks.description(brokenLinkIssues.length)}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {brokenLinkIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full border border-success-400/20 bg-success-500/10"><FontAwesomeIcon icon={faLink} className="text-2xl text-success-400" /></div>
            <h3 className="text-xl font-semibold tracking-tight text-success-300 mb-2">{t.sections.brokenLinks.emptyTitle}</h3>
            <p className="text-muted-foreground">{t.sections.brokenLinks.emptyBody}</p>
          </div>
        ) : (
          <>
            <Tabs
              ariaLabel={t.sections.brokenLinks.title}
              tabs={[
                { id: 'internal', label: t.sections.brokenLinks.tabs.internal, count: internalLinks.length },
                { id: 'external', label: t.sections.brokenLinks.tabs.external, count: externalLinks.length },
              ]}
              active={activeTab}
              onChange={setActiveTab}
            />

            <div className="space-y-4">
              {currentIssues.slice(0, pagination.visible).map((issue) => (
                <IssueCard key={issue.id} issue={issue} sourceMode="text" />
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
                {t.sections.brokenLinks.emptyTab[activeTab]}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}

