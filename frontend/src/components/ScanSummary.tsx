import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { getGradeColor } from '../issueMeta'
import type { ScanResults, SEOGrade } from '../types'

interface ScanSummaryProps {
  results: ScanResults
  seoGrade: SEOGrade | null
}

export function ScanSummary({ results, seoGrade }: ScanSummaryProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Scan Summary</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="p-4 rounded-lg bg-secondary-600/10 border border-secondary-600/20">
            <div className="text-sm text-muted-foreground mb-1">URL</div>
            <div className="font-semibold text-sm truncate">{results.scan.url}</div>
          </div>
          <div className="p-4 rounded-lg bg-secondary-600/10 border border-secondary-600/20 col-span-1">
            <div className="text-sm text-muted-foreground mb-1">Pages Analyzed</div>
            <div className="text-2xl font-bold text-primary-400">{results.scan.total_pages}</div>
          </div>
          <div className="p-4 rounded-lg bg-secondary-600/10 border border-secondary-600/20 col-span-1">
            <div className="text-sm text-muted-foreground mb-1">Total Issues</div>
            <div className={`text-2xl font-bold ${results.scan.total_issues === 0 ? "text-emerald-400" : "text-accent-400"}`}>{results.scan.total_issues}</div>
          </div>

          {seoGrade && (
            <div className="p-4 rounded-lg bg-secondary-600/10 border border-secondary-600/20 col-span-1">
              <div className="text-sm text-muted-foreground mb-1">SEO Grade</div>
              <div className={`text-2xl font-bold ${getGradeColor(seoGrade.grade)}`}>
                {seoGrade.grade}
              </div>
            </div>
          )}

          <div className="p-4 rounded-lg bg-secondary-600/10 border border-secondary-600/20">
            <div className="text-sm text-muted-foreground mb-1">Scan Time</div>
            <div className="text-sm font-semibold">{new Date(results.scan.timestamp).toLocaleString()}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
