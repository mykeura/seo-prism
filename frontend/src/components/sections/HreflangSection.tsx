import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faGlobe } from '@fortawesome/free-solid-svg-icons'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import { getHreflangIssues } from '../../filters'
import type { Issue } from '../../types'

export function HreflangSection({ issues }: { issues: Issue[] }) {
  const pagination = usePagination()

  const hreflangIssues = getHreflangIssues(issues)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Hreflang Validation</CardTitle>
        <CardDescription>
          {hreflangIssues.length} hreflang issue{hreflangIssues.length !== 1 ? 's' : ''} found
        </CardDescription>
      </CardHeader>
      <CardContent>
        {hreflangIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full border border-success-400/20 bg-success-500/10"><FontAwesomeIcon icon={faGlobe} className="text-2xl text-success-400" /></div>
            <h3 className="text-xl font-semibold tracking-tight text-success-300 mb-2">No Hreflang Issues Found!</h3>
            <p className="text-muted-foreground">All hreflang tags are properly configured.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {hreflangIssues.slice(0, pagination.visible).map((issue) => (
              <IssueCard key={issue.id} issue={issue} sourceMode="text-if-different" />
            ))}
            {pagination.hasMore(hreflangIssues.length) && (
              <div className="text-center mt-4">
                <ShowMoreButton
                  visible={pagination.visible}
                  total={hreflangIssues.length}
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
