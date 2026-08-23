import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faFileImage } from '@fortawesome/free-solid-svg-icons'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import { getMissingAltTagIssues } from '../../filters'
import type { Issue } from '../../types'

export function ImagesAltSection({ issues }: { issues: Issue[] }) {
  const pagination = usePagination()

  const missingAltTagIssues = getMissingAltTagIssues(issues)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Images Without Alt</CardTitle>
        <CardDescription>
          {missingAltTagIssues.length} image{missingAltTagIssues.length !== 1 ? 's' : ''} missing alt tag{missingAltTagIssues.length !== 1 ? 's' : ''}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {missingAltTagIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full border border-success-400/20 bg-success-500/10"><FontAwesomeIcon icon={faFileImage} className="text-2xl text-success-400" /></div>
            <h3 className="text-xl font-semibold tracking-tight text-success-300 mb-2">All Images Have Alt Tags!</h3>
            <p className="text-muted-foreground">All images have proper alt tags for SEO and accessibility.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {missingAltTagIssues.slice(0, pagination.visible).map((issue) => (
              <IssueCard
                key={issue.id}
                issue={issue}
                urlLabel="Image URL:"
                sourceMode="link"
                sourceLabel="Found on page:"
              />
            ))}
            {pagination.hasMore(missingAltTagIssues.length) && (
              <div className="text-center mt-4">
                <ShowMoreButton
                  visible={pagination.visible}
                  total={missingAltTagIssues.length}
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
