import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faDatabase } from '@fortawesome/free-solid-svg-icons'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import { getStructuredDataIssues } from '../../filters'
import type { Issue } from '../../types'

export function StructuredDataSection({ issues }: { issues: Issue[] }) {
  const pagination = usePagination()

  const structuredDataIssues = getStructuredDataIssues(issues)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Structured Data</CardTitle>
        <CardDescription>
          {structuredDataIssues.length} structured data issue{structuredDataIssues.length !== 1 ? 's' : ''} detected
        </CardDescription>
      </CardHeader>
      <CardContent>
        {structuredDataIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-4"><FontAwesomeIcon icon={faDatabase} className="text-primary-400" /></div>
            <h3 className="text-xl font-semibold text-emerald-400 mb-2">No Structured Data Issues Found!</h3>
            <p className="text-muted-foreground">All structured data is properly configured.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {structuredDataIssues.slice(0, pagination.visible).map((issue) => (
              <IssueCard key={issue.id} issue={issue} />
            ))}
            {pagination.hasMore(structuredDataIssues.length) && (
              <div className="text-center mt-4">
                <ShowMoreButton
                  visible={pagination.visible}
                  total={structuredDataIssues.length}
                  label="structured data issues"
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
