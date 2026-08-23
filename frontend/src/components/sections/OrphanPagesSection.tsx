import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faFolder } from '@fortawesome/free-solid-svg-icons'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import { getOrphanPagesIssues } from '../../filters'
import type { Issue } from '../../types'

export function OrphanPagesSection({ issues }: { issues: Issue[] }) {
  const pagination = usePagination()

  const orphanPagesIssues = getOrphanPagesIssues(issues)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Orphan Pages</CardTitle>
        <CardDescription>
          {orphanPagesIssues.length} orphan page{orphanPagesIssues.length !== 1 ? 's' : ''} detected
        </CardDescription>
      </CardHeader>
      <CardContent>
        {orphanPagesIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-4"><FontAwesomeIcon icon={faFolder} className="text-primary-400" /></div>
            <h3 className="text-xl font-semibold text-emerald-400 mb-2">No Orphan Pages Found!</h3>
            <p className="text-muted-foreground">All pages have incoming internal links.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {orphanPagesIssues.slice(0, pagination.visible).map((issue) => (
              <IssueCard key={issue.id} issue={issue} />
            ))}
            {pagination.hasMore(orphanPagesIssues.length) && (
              <div className="text-center mt-4">
                <ShowMoreButton
                  visible={pagination.visible}
                  total={orphanPagesIssues.length}
                  label="orphan pages"
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
