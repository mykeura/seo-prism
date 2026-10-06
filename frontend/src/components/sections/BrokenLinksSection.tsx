// SPDX-License-Identifier: AGPL-3.0-only
// SPDX-FileCopyrightText: 2026 mykeura <mykeura@hotmail.com>

import { useState } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faLink } from '@fortawesome/free-solid-svg-icons'
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
            <div className="flex gap-2 mb-4 border-b border-border">
              <button
                onClick={() => setActiveTab('internal')}
                className={`px-4 py-2 font-medium transition-colors ${
                  activeTab === 'internal'
                    ? 'text-primary-300 -mb-px border-b-2 border-primary-400 spectrum-underline'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {t.sections.brokenLinks.tabs.internal} ({internalLinks.length})
              </button>
              <button
                onClick={() => setActiveTab('external')}
                className={`px-4 py-2 font-medium transition-colors ${
                  activeTab === 'external'
                    ? 'text-primary-300 -mb-px border-b-2 border-primary-400 spectrum-underline'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {t.sections.brokenLinks.tabs.external} ({externalLinks.length})
              </button>
            </div>

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

