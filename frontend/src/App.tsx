// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { useMemo, useState, type FormEvent } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCircleCheck } from '@fortawesome/free-solid-svg-icons'
import { Card, CardContent } from './components/ui/card'
import { AppHeader } from './components/AppHeader'
import { ExportCsvButton } from './components/ExportCsvButton'
import { Hero } from './components/Hero'
import { ScanForm } from './components/ScanForm'
import { ScanHistory } from './components/ScanHistory'
import { ScanOverview } from './components/ScanOverview'
import { SectionNav } from './components/SectionNav'
import { SECTIONS, defaultSectionId, summarizeSections } from './sections'
import { apiFetch } from './lib/api'
import { normalizeUrl } from './lib/url'
import { readErrorDetail } from './hooks/useScanHistory'
import type { SEOGrade, ScanResults } from './types'
import { useT } from './i18n'
import { APP_VERSION } from './version'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function App() {
  const t = useT()

  const [results, setResults] = useState<ScanResults | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [seoGrade, setSeoGrade] = useState<SEOGrade | null>(null)
  const [url, setUrl] = useState('')
  const [selectedSection, setSelectedSection] = useState<string | null>(null)
  const [historyOpen, setHistoryOpen] = useState(false)
  // Bumped after a scan succeeds so an open history panel refetches /scans.
  const [historyVersion, setHistoryVersion] = useState(0)

  const summaries = useMemo(() => (results ? summarizeSections(results) : []), [results])
  const activeSectionId =
    selectedSection && summaries.some((s) => s.id === selectedSection)
      ? selectedSection
      : defaultSectionId(summaries)
  const activeSection = SECTIONS.find((section) => section.id === activeSectionId)
  const hasActionableIssues = summaries.some((summary) => summary.count > 0)

  const handleScan = async (e: FormEvent) => {
    e.preventDefault()
    const target = normalizeUrl(url)
    if (!target) return

    setUrl(target)
    setLoading(true)
    setError(null)
    setMessage(null)
    setResults(null)
    setSeoGrade(null)
    setSelectedSection(null)

    try {
      const scanResponse = await apiFetch(`${API_BASE_URL}/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: target }),
      })

      if (!scanResponse.ok) {
        if (scanResponse.status === 401) throw new Error(t.apiKey.required)
        const detail = await readErrorDetail(scanResponse)
        throw new Error(detail ? `${t.app.startScanFailed}: ${detail}` : t.app.startScanFailed)
      }

      const scanData = await scanResponse.json()
      setMessage(scanData.message)
      if (scanData.seo_grade) {
        setSeoGrade(scanData.seo_grade)
      }

      // Ask for this scan by id: "latest" could be another scan if two
      // were started close together.
      const resultsPath = scanData.scan_id != null ? `/results/${scanData.scan_id}` : '/results'
      const resultsResponse = await apiFetch(`${API_BASE_URL}${resultsPath}`)

      if (!resultsResponse.ok) {
        if (resultsResponse.status === 401) throw new Error(t.apiKey.required)
        throw new Error(t.app.resultsFailed)
      }

      setResults(await resultsResponse.json())
      setHistoryVersion((version) => version + 1)
    } catch (err) {
      if (err instanceof TypeError) {
        // fetch() rejects with TypeError when the server cannot be reached
        setError(t.app.backendUnreachable(API_BASE_URL))
      } else {
        setError(err instanceof Error ? err.message : t.app.genericError)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleLoadScan = async (scanId: number, grade?: Pick<SEOGrade, 'grade' | 'score'>) => {
    setLoading(true)
    setError(null)
    setMessage(null)
    setResults(null)
    setSeoGrade(null)
    setSelectedSection(null)

    try {
      const resultsResponse = await apiFetch(`${API_BASE_URL}/results/${scanId}`)

      if (!resultsResponse.ok) {
        if (resultsResponse.status === 401) throw new Error(t.apiKey.required)
        throw new Error(t.app.resultsFailed)
      }

      const data: ScanResults = await resultsResponse.json()
      setResults(data)
      // The history row carries letter and score only; the gauge reads just
      // those, so a zeroed breakdown stands in for the absent detail.
      setSeoGrade(
        data.seo_grade ??
          (grade ? { ...grade, breakdown: { high: 0, medium: 0, low: 0, total: 0 } } : null),
      )
      setUrl(data.scan.url)
    } catch (err) {
      if (err instanceof TypeError) {
        // fetch() rejects with TypeError when the server cannot be reached
        setError(t.app.backendUnreachable(API_BASE_URL))
      } else {
        setError(err instanceof Error ? err.message : t.app.genericError)
      }
    } finally {
      setLoading(false)
    }
  }

  const scanForm = (variant: 'hero' | 'compact') => (
    <ScanForm
      url={url}
      onUrlChange={setUrl}
      onSubmit={handleScan}
      loading={loading}
      message={message}
      error={error}
      variant={variant}
    />
  )

  return (
    <div className="min-h-screen bg-background font-sans text-foreground">
      {/* Aurora prism backdrop: fixed refracted-light blobs (pure CSS) */}
      <div aria-hidden="true" className="prisma-aurora" />

      <div className="container mx-auto max-w-6xl px-4 pb-10">
        <AppHeader historyOpen={historyOpen} onToggleHistory={() => setHistoryOpen((open) => !open)} />

        {historyOpen && (
          <div id="scan-history" className="pb-6">
            <ScanHistory
              apiBaseUrl={API_BASE_URL}
              loading={loading}
              refreshKey={historyVersion}
              onLoadScan={handleLoadScan}
            />
          </div>
        )}

        {results ? (
          <main className="space-y-6 pt-2">
            {scanForm('compact')}

            <ScanOverview results={results} seoGrade={seoGrade} />

            {!hasActionableIssues && (
              <Card className="border-success-400/20 bg-success-500/[0.04]">
                <CardContent className="flex items-center gap-4 p-5 sm:p-6">
                  <span className="inline-flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-success-400/25 bg-success-500/10 text-xl text-success-300">
                    <FontAwesomeIcon icon={faCircleCheck} aria-hidden="true" />
                  </span>
                  <div>
                    <h2 className="font-display text-lg font-semibold tracking-tight text-success-300">
                      {t.app.noIssuesTitle}
                    </h2>
                    <p className="text-sm text-muted-foreground">{t.app.noIssuesBody}</p>
                  </div>
                </CardContent>
              </Card>
            )}

            <div className="grid gap-6 lg:grid-cols-[15.5rem_minmax(0,1fr)] lg:items-start">
              <SectionNav
                summaries={summaries}
                activeId={activeSectionId}
                onSelect={setSelectedSection}
              />
              <div className="min-w-0">
                {activeSection && (
                  <div className="mb-3 flex justify-end">
                    <ExportCsvButton
                      issues={activeSection.issues(results)}
                      filename={`seo-prism-${activeSection.id}-${results.scan.id}.csv`}
                    />
                  </div>
                )}
                {activeSection?.render(results)}
              </div>
            </div>
          </main>
        ) : (
          <main className="pb-6 pt-2">
            <Hero scanning={loading} />
            {scanForm('hero')}
            <ul
              aria-label={t.hero.checksLabel}
              className="mx-auto mt-10 flex max-w-3xl flex-wrap justify-center gap-2"
            >
              {SECTIONS.map((section) => (
                <li
                  key={section.id}
                  className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-sm text-muted-foreground"
                >
                  <FontAwesomeIcon icon={section.icon} className="text-xs text-primary-300" aria-hidden="true" />
                  {section.title(t)}
                </li>
              ))}
            </ul>
          </main>
        )}

        <footer className="mt-16 border-t border-white/5 pt-6 text-center text-sm text-muted-foreground">
          {t.app.footer(APP_VERSION)}
        </footer>
      </div>
    </div>
  )
}

export default App
