import { useState } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faFileAlt } from '@fortawesome/free-solid-svg-icons'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import { getMetaTagsIssues, getMissingDescriptions, getMissingTitles } from '../../filters'
import type { Issue } from '../../types'

export function MetaTagsSection({ issues }: { issues: Issue[] }) {
  const [metaTab, setMetaTab] = useState<'titles' | 'descriptions'>('titles')
  const pagination = usePagination()

  const metaTagsIssues = getMetaTagsIssues(issues)
  const missingTitles = getMissingTitles(metaTagsIssues)
  const missingDescriptions = getMissingDescriptions(metaTagsIssues)
  const currentIssues = metaTab === 'titles' ? missingTitles : missingDescriptions

  return (
    <Card>
      <CardHeader>
        <CardTitle>Meta Tags Issues</CardTitle>
        <CardDescription>
          {metaTagsIssues.length} meta tag issue{metaTagsIssues.length !== 1 ? 's' : ''} detected
        </CardDescription>
      </CardHeader>
      <CardContent>
        {metaTagsIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full border border-success-400/20 bg-success-500/10"><FontAwesomeIcon icon={faFileAlt} className="text-2xl text-success-400" /></div>
            <h3 className="text-xl font-semibold tracking-tight text-success-300 mb-2">No Meta Tag Issues Found!</h3>
            <p className="text-muted-foreground">All pages have proper title tags and descriptions.</p>
          </div>
        ) : (
          <>
            <div className="flex gap-2 mb-4 border-b border-border">
              <button
                onClick={() => setMetaTab('titles')}
                className={`px-4 py-2 font-medium transition-colors ${
                  metaTab === 'titles'
                    ? 'text-primary-300 -mb-px border-b-2 border-primary-400 spectrum-underline'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Missing Titles ({missingTitles.length})
              </button>
              <button
                onClick={() => setMetaTab('descriptions')}
                className={`px-4 py-2 font-medium transition-colors ${
                  metaTab === 'descriptions'
                    ? 'text-primary-300 -mb-px border-b-2 border-primary-400 spectrum-underline'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Missing Descriptions ({missingDescriptions.length})
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
                No {metaTab === 'titles' ? 'missing titles' : 'missing descriptions'} found
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}
