import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { getGradeColor } from '../issueMeta'
import { useT } from '../i18n'
import type { ScanResults, SEOGrade } from '../types'

interface ScanSummaryProps {
  results: ScanResults
  seoGrade: SEOGrade | null
}

export function ScanSummary({ results, seoGrade }: ScanSummaryProps) {
  const t = useT()
  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.summary.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4 transition-colors duration-200 hover:border-white/20">
            <div className="mb-1.5 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">{t.summary.url}</div>
            <div className="truncate text-sm font-semibold" title={results.scan.url}>{results.scan.url}</div>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4 transition-colors duration-200 hover:border-white/20">
            <div className="mb-1.5 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">{t.summary.pagesAnalyzed}</div>
            <div className="text-3xl font-bold tracking-tight text-primary-300">{results.scan.total_pages}</div>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4 transition-colors duration-200 hover:border-white/20">
            <div className="mb-1.5 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">{t.summary.totalIssues}</div>
            <div className={`text-3xl font-bold tracking-tight ${results.scan.total_issues === 0 ? 'text-success-300' : 'text-accent-300'}`}>{results.scan.total_issues}</div>
          </div>

          {seoGrade && (
            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4 transition-colors duration-200 hover:border-white/20">
              <div className="mb-1.5 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">{t.summary.seoGrade}</div>
              <div className={`inline-flex h-11 w-11 items-center justify-center rounded-xl border text-2xl font-extrabold tracking-tight ${getGradeColor(seoGrade.grade)}`}>
                {seoGrade.grade}
              </div>
            </div>
          )}

          <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4 transition-colors duration-200 hover:border-white/20">
            <div className="mb-1.5 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">{t.summary.scanTime}</div>
            <div className="text-sm font-semibold leading-7">{new Date(results.scan.timestamp).toLocaleString()}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
