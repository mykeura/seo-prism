import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faFileAlt } from '@fortawesome/free-solid-svg-icons'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { IssueCard } from '../IssueCard'
import { ShowMoreButton } from '../ShowMoreButton'
import { usePagination } from '../../hooks/usePagination'
import { getThinContentIssues } from '../../filters'
import { useT } from '../../i18n'
import type { Issue } from '../../types'

export function ThinContentSection({ issues }: { issues: Issue[] }) {
  const t = useT()
  const pagination = usePagination()

  const thinContentIssues = getThinContentIssues(issues)

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.sections.thinContent.title}</CardTitle>
        <CardDescription>
          {t.sections.thinContent.description(thinContentIssues.length)}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {thinContentIssues.length === 0 ? (
          <div className="text-center py-8">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full border border-success-400/20 bg-success-500/10"><FontAwesomeIcon icon={faFileAlt} className="text-2xl text-success-400" /></div>
            <h3 className="text-xl font-semibold tracking-tight text-success-300 mb-2">{t.sections.thinContent.emptyTitle}</h3>
            <p className="text-muted-foreground">{t.sections.thinContent.emptyBody}</p>
          </div>
        ) : (
          <div className="space-y-4">
            {thinContentIssues.slice(0, pagination.visible).map((issue) => (
              <IssueCard key={issue.id} issue={issue} />
            ))}
            {pagination.hasMore(thinContentIssues.length) && (
              <div className="text-center mt-4">
                <ShowMoreButton
                  visible={pagination.visible}
                  total={thinContentIssues.length}
                  label={t.sections.thinContent.showMoreLabel}
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
