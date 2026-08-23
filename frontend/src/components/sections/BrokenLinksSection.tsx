import { useState } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faLink } from '@fortawesome/free-solid-svg-icons'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import { getBrokenLinkIssues, getExternalLinks, getInternalLinks } from '../../filters'
import type { ScanResults } from '../../types'

export function BrokenLinksSection({ results }: { results: ScanResults }) {
  const [activeTab, setActiveTab] = useState<'internal' | 'external'>('internal')
  const pagination = usePagination()

  const brokenLinkIssues = getBrokenLinkIssues(results.issues)
  const internalLinks = getInternalLinks(brokenLinkIssues, results.scan.url)
  const externalLinks = getExternalLinks(brokenLinkIssues, results.scan.url)
  const currentIssues = activeTab === 'internal' ? internalLinks : externalLinks

  return (
    <Card>
      <CardHeader>
        <CardTitle>Broken Links</CardTitle>
        <CardDescription>
          {brokenLinkIssues.length} broken link{brokenLinkIssues.length !== 1 ? 's' : ''} detected
        </CardDescription>
      </CardHeader>
      <CardContent>
        {brokenLinkIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-4"><FontAwesomeIcon icon={faLink} className="text-primary-400" /></div>
            <h3 className="text-xl font-semibold text-emerald-400 mb-2">No Broken Links Found!</h3>
            <p className="text-muted-foreground">All internal and external links are working correctly.</p>
          </div>
        ) : (
          <>
            <div className="flex gap-2 mb-4 border-b border-border">
              <button
                onClick={() => setActiveTab('internal')}
                className={`px-4 py-2 font-medium transition-colors ${
                  activeTab === 'internal'
                    ? 'text-primary-400 border-b-2 border-primary-400'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Internal Links ({internalLinks.length})
              </button>
              <button
                onClick={() => setActiveTab('external')}
                className={`px-4 py-2 font-medium transition-colors ${
                  activeTab === 'external'
                    ? 'text-primary-400 border-b-2 border-primary-400'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                External Links ({externalLinks.length})
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
                No {activeTab === 'internal' ? 'internal' : 'external'} broken links found
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}

