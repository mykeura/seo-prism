import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faFolder } from '@fortawesome/free-solid-svg-icons'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import { getStandardFilesIssues } from '../../filters'
import type { Issue } from '../../types'

export function StandardFilesSection({ issues }: { issues: Issue[] }) {
  const pagination = usePagination()

  const standardFilesIssues = getStandardFilesIssues(issues)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Standard Files</CardTitle>
        <CardDescription>
          {standardFilesIssues.length} standard file{standardFilesIssues.length !== 1 ? 's' : ''} found
        </CardDescription>
      </CardHeader>
      <CardContent>
        {standardFilesIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full border border-white/10 bg-white/[0.04]"><FontAwesomeIcon icon={faFolder} className="text-2xl text-primary-300" /></div>
            <h3 className="text-xl font-semibold tracking-tight text-muted-foreground mb-2">No Standard Files Found</h3>
            <p className="text-muted-foreground">No robots.txt, security.txt or sitemap files were detected.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {standardFilesIssues.slice(0, pagination.visible).map((issue) => (
              <IssueCard key={issue.id} issue={issue} tone="success" />
            ))}
            {pagination.hasMore(standardFilesIssues.length) && (
              <div className="text-center mt-4">
                <ShowMoreButton
                  visible={pagination.visible}
                  total={standardFilesIssues.length}
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
