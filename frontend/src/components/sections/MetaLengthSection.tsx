import { useState } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faFileAlt } from '@fortawesome/free-solid-svg-icons'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import { getMetaDescLengthIssues, getMetaLengthIssues, getTitleLengthIssues } from '../../filters'
import type { Issue } from '../../types'

export function MetaLengthSection({ issues }: { issues: Issue[] }) {
  const [metaLengthTab, setMetaLengthTab] = useState<'titles' | 'descriptions'>('titles')
  const pagination = usePagination()

  const metaLengthIssues = getMetaLengthIssues(issues)
  const titleLengthIssues = getTitleLengthIssues(metaLengthIssues)
  const metaDescLengthIssues = getMetaDescLengthIssues(metaLengthIssues)
  const currentIssues = metaLengthTab === 'titles' ? titleLengthIssues : metaDescLengthIssues

  return (
    <Card>
      <CardHeader>
        <CardTitle>Meta Length Analysis</CardTitle>
        <CardDescription>
          {metaLengthIssues.length} meta length issue{metaLengthIssues.length !== 1 ? 's' : ''} detected
        </CardDescription>
      </CardHeader>
      <CardContent>
        {metaLengthIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-4"><FontAwesomeIcon icon={faFileAlt} className="text-primary-400" /></div>
            <h3 className="text-xl font-semibold text-emerald-400 mb-2">All Meta Tags Have Optimal Length!</h3>
            <p className="text-muted-foreground">All titles and meta descriptions have the recommended length.</p>
          </div>
        ) : (
          <>
            <div className="flex gap-2 mb-4 border-b border-border">
              <button
                onClick={() => setMetaLengthTab('titles')}
                className={`px-4 py-2 font-medium transition-colors ${
                  metaLengthTab === 'titles'
                    ? 'text-primary-400 border-b-2 border-primary-400'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Title Length ({titleLengthIssues.length})
              </button>
              <button
                onClick={() => setMetaLengthTab('descriptions')}
                className={`px-4 py-2 font-medium transition-colors ${
                  metaLengthTab === 'descriptions'
                    ? 'text-primary-400 border-b-2 border-primary-400'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Description Length ({metaDescLengthIssues.length})
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
                No {metaLengthTab === 'titles' ? 'title length' : 'description length'} issues found
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}
