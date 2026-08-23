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
import type { Issue } from '../../types'

type CanonicalTab = 'all' | 'chains' | '404' | 'redirect' | 'variations' | 'missing'

export function CanonicalSection({ issues }: { issues: Issue[] }) {
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
        <CardTitle>Canonical Tags</CardTitle>
        <CardDescription>
          {canonicalIssues.length} canonical issue{canonicalIssues.length !== 1 ? 's' : ''} found
        </CardDescription>
      </CardHeader>
      <CardContent>
        {canonicalIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-4"><FontAwesomeIcon icon={faLink} className="text-primary-400" /></div>
            <h3 className="text-xl font-semibold text-emerald-400 mb-2">No Canonical Issues Found!</h3>
            <p className="text-muted-foreground">All canonical tags are properly configured.</p>
          </div>
        ) : (
          <>
            <div className="flex gap-2 mb-4 border-b border-border flex-wrap">
              <button
                onClick={() => setCanonicalTab('all')}
                className={`px-4 py-2 font-medium transition-colors ${
                  canonicalTab === 'all'
                    ? 'text-primary-400 border-b-2 border-primary-400'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                All ({canonicalIssues.length})
              </button>
              <button
                onClick={() => setCanonicalTab('chains')}
                className={`px-4 py-2 font-medium transition-colors ${
                  canonicalTab === 'chains'
                    ? 'text-primary-400 border-b-2 border-primary-400'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Chains ({canonicalChains.length})
              </button>
              <button
                onClick={() => setCanonicalTab('404')}
                className={`px-4 py-2 font-medium transition-colors ${
                  canonicalTab === '404'
                    ? 'text-primary-400 border-b-2 border-primary-400'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                404 ({canonical404.length})
              </button>
              <button
                onClick={() => setCanonicalTab('redirect')}
                className={`px-4 py-2 font-medium transition-colors ${
                  canonicalTab === 'redirect'
                    ? 'text-primary-400 border-b-2 border-primary-400'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Redirects ({canonicalRedirect.length})
              </button>
              <button
                onClick={() => setCanonicalTab('variations')}
                className={`px-4 py-2 font-medium transition-colors ${
                  canonicalTab === 'variations'
                    ? 'text-primary-400 border-b-2 border-primary-400'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Variations ({canonicalVariations.length})
              </button>
              <button
                onClick={() => setCanonicalTab('missing')}
                className={`px-4 py-2 font-medium transition-colors ${
                  canonicalTab === 'missing'
                    ? 'text-primary-400 border-b-2 border-primary-400'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Missing ({missingCanonical.length})
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
                No {canonicalTab === 'all' ? 'canonical' :
                    canonicalTab === 'chains' ? 'canonical chain' :
                    canonicalTab === '404' ? 'canonical 404' :
                    canonicalTab === 'redirect' ? 'canonical redirect' :
                    canonicalTab === 'variations' ? 'canonical variation' : 'missing canonical'} issues found
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}
