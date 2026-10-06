// SPDX-License-Identifier: AGPL-3.0-only
// SPDX-FileCopyrightText: 2026 mykeura <mykeura@hotmail.com>

import { useState } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faLink } from '@fortawesome/free-solid-svg-icons'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import {
  getCanonical404,
  getCanonicalChains,
  getCanonicalIssues,
  getCanonicalRedirect,
  getCanonicalVariations,
  getMissingCanonical,
} from '../../filters'
import { useT } from '../../i18n'
import type { Issue } from '../../types'

type CanonicalTab = 'all' | 'chains' | '404' | 'redirect' | 'variations' | 'missing'

export function CanonicalSection({ issues }: { issues: Issue[] }) {
  const t = useT()
  const [canonicalTab, setCanonicalTab] = useState<CanonicalTab>('all')
  const pagination = usePagination()

  const canonicalIssues = getCanonicalIssues(issues)
  const canonicalChains = getCanonicalChains(canonicalIssues)
  const canonical404 = getCanonical404(canonicalIssues)
  const canonicalRedirect = getCanonicalRedirect(canonicalIssues)
  const canonicalVariations = getCanonicalVariations(canonicalIssues)
  const missingCanonical = getMissingCanonical(canonicalIssues)

  const currentIssues =
    canonicalTab === 'all' ? canonicalIssues :
    canonicalTab === 'chains' ? canonicalChains :
    canonicalTab === '404' ? canonical404 :
    canonicalTab === 'redirect' ? canonicalRedirect :
    canonicalTab === 'variations' ? canonicalVariations :
    missingCanonical

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.sections.canonical.title}</CardTitle>
        <CardDescription>
          {t.sections.canonical.description(canonicalIssues.length)}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {canonicalIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full border border-success-400/20 bg-success-500/10"><FontAwesomeIcon icon={faLink} className="text-2xl text-success-400" /></div>
            <h3 className="text-xl font-semibold tracking-tight text-success-300 mb-2">{t.sections.canonical.emptyTitle}</h3>
            <p className="text-muted-foreground">{t.sections.canonical.emptyBody}</p>
          </div>
        ) : (
          <>
            <div className="flex gap-2 mb-4 border-b border-border flex-wrap">
              <button
                onClick={() => setCanonicalTab('all')}
                className={`px-4 py-2 font-medium transition-colors ${
                  canonicalTab === 'all'
                    ? 'text-primary-300 -mb-px border-b-2 border-primary-400 spectrum-underline'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {t.sections.canonical.tabs.all} ({canonicalIssues.length})
              </button>
              <button
                onClick={() => setCanonicalTab('chains')}
                className={`px-4 py-2 font-medium transition-colors ${
                  canonicalTab === 'chains'
                    ? 'text-primary-300 -mb-px border-b-2 border-primary-400 spectrum-underline'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {t.sections.canonical.tabs.chains} ({canonicalChains.length})
              </button>
              <button
                onClick={() => setCanonicalTab('404')}
                className={`px-4 py-2 font-medium transition-colors ${
                  canonicalTab === '404'
                    ? 'text-primary-300 -mb-px border-b-2 border-primary-400 spectrum-underline'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                404 ({canonical404.length})
              </button>
              <button
                onClick={() => setCanonicalTab('redirect')}
                className={`px-4 py-2 font-medium transition-colors ${
                  canonicalTab === 'redirect'
                    ? 'text-primary-300 -mb-px border-b-2 border-primary-400 spectrum-underline'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {t.sections.canonical.tabs.redirect} ({canonicalRedirect.length})
              </button>
              <button
                onClick={() => setCanonicalTab('variations')}
                className={`px-4 py-2 font-medium transition-colors ${
                  canonicalTab === 'variations'
                    ? 'text-primary-300 -mb-px border-b-2 border-primary-400 spectrum-underline'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {t.sections.canonical.tabs.variations} ({canonicalVariations.length})
              </button>
              <button
                onClick={() => setCanonicalTab('missing')}
                className={`px-4 py-2 font-medium transition-colors ${
                  canonicalTab === 'missing'
                    ? 'text-primary-300 -mb-px border-b-2 border-primary-400 spectrum-underline'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {t.sections.canonical.tabs.missing} ({missingCanonical.length})
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
                {t.sections.canonical.emptyTab[canonicalTab]}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}
