import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faRobot } from '@fortawesome/free-solid-svg-icons'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import { getMetaRobotsIssues } from '../../filters'
import type { Issue } from '../../types'

export function MetaRobotsSection({ issues }: { issues: Issue[] }) {
  const pagination = usePagination()

  const metaRobotsIssues = getMetaRobotsIssues(issues)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Meta Robots Directives</CardTitle>
        <CardDescription>
          {metaRobotsIssues.length} meta robots issue{metaRobotsIssues.length !== 1 ? 's' : ''} found
        </CardDescription>
      </CardHeader>
      <CardContent>
        {metaRobotsIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full border border-success-400/20 bg-success-500/10"><FontAwesomeIcon icon={faRobot} className="text-2xl text-success-400" /></div>
            <h3 className="text-xl font-semibold tracking-tight text-success-300 mb-2">No Meta Robots Issues Found!</h3>
            <p className="text-muted-foreground">No restrictive meta robots directives detected.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {metaRobotsIssues.slice(0, pagination.visible).map((issue) => (
              <IssueCard key={issue.id} issue={issue} sourceMode="text-if-different" />
            ))}
            {pagination.hasMore(metaRobotsIssues.length) && (
              <div className="text-center mt-4">
                <ShowMoreButton
                  visible={pagination.visible}
                  total={metaRobotsIssues.length}
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
