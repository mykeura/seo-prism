import { useState } from 'react'
import { Card, CardContent, CardFooter } from './components/ui/card'
import { ScanForm } from './components/ScanForm'
import { ScanSummary } from './components/ScanSummary'
import { BrokenLinksSection } from './components/sections/BrokenLinksSection'
import { MetaTagsSection } from './components/sections/MetaTagsSection'
import { MetaLengthSection } from './components/sections/MetaLengthSection'
import { ImagesAltSection } from './components/sections/ImagesAltSection'
import { HeaderAnalysisSection } from './components/sections/HeaderAnalysisSection'
import { StandardFilesSection } from './components/sections/StandardFilesSection'
import { MetaRobotsSection } from './components/sections/MetaRobotsSection'
import { HreflangSection } from './components/sections/HreflangSection'
import { CanonicalSection } from './components/sections/CanonicalSection'
import { OrphanPagesSection } from './components/sections/OrphanPagesSection'
import { StructuredDataSection } from './components/sections/StructuredDataSection'
import { ThinContentSection } from './components/sections/ThinContentSection'
import type { SEOGrade, ScanResults } from './types'

function App() {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

  const [results, setResults] = useState<ScanResults | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [seoGrade, setSeoGrade] = useState<SEOGrade | null>(null)
  const [url, setUrl] = useState('')

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setError(null)
    setMessage(null)
    setResults(null)

    try {
      const scanResponse = await fetch(`${API_BASE_URL}/scan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      })

      if (!scanResponse.ok) {
        throw new Error('Failed to start scan')
      }

      const scanData = await scanResponse.json()
      setMessage(scanData.message)

      // Store SEO grade from scan response
      if (scanData.seo_grade) {
        setSeoGrade(scanData.seo_grade)
      }

      const resultsResponse = await fetch(`${API_BASE_URL}/results`)

      if (!resultsResponse.ok) {
        throw new Error('Failed to get results')
      }

      const resultsData = await resultsResponse.json()
      setResults(resultsData)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background font-sans text-foreground">
      {/* Aurora prism backdrop: fixed refracted-light blobs (pure CSS) */}
      <div aria-hidden="true" className="prisma-aurora" />

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <header className="mb-12 pt-6 text-center">
          <h1 className="mb-3 bg-linear-to-r from-cyan-300 via-primary-300 via-secondary-400 to-accent-400 bg-clip-text text-5xl font-extrabold tracking-tight text-transparent drop-shadow-[0_0_28px_rgba(99,102,241,0.3)]">
            SEO Prism
          </h1>
          <p className="mx-auto max-w-2xl text-balance text-base leading-relaxed text-muted-foreground">
            Comprehensive SEO analysis: broken links, meta tags, duplicate content, header hierarchy, structured data and more
          </p>
        </header>

        <ScanForm
          url={url}
          onUrlChange={setUrl}
          onSubmit={handleScan}
          loading={loading}
          message={message}
          error={error}
        />

        {results && (
          <div className="space-y-6">
            <ScanSummary results={results} seoGrade={seoGrade} />

            {results.issues.length === 0 ? (
              <Card className="border-success-400/20 bg-success-500/[0.04]">
                <CardContent className="pt-6">
                  <div className="text-center py-8">
                    <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full border border-success-400/25 bg-success-500/10 text-3xl">✅</div>
                    <h3 className="text-xl font-semibold tracking-tight text-success-300 mb-2">No Issues Found!</h3>
                    <p className="text-muted-foreground">Your website looks great!</p>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <>
                <BrokenLinksSection results={results} />
                <MetaTagsSection issues={results.issues} />
                <MetaLengthSection issues={results.issues} />
                <ImagesAltSection issues={results.issues} />
                <HeaderAnalysisSection issues={results.issues} />
                <StandardFilesSection issues={results.issues} />
                <MetaRobotsSection issues={results.issues} />
                <HreflangSection issues={results.issues} />
                <CanonicalSection issues={results.issues} />
                <OrphanPagesSection issues={results.issues} />
                <StructuredDataSection issues={results.issues} />
                <ThinContentSection issues={results.issues} />
              </>
            )}
          </div>
        )}

        <footer className="mt-12 text-center">
          <Card className="opacity-90">
            <CardFooter className="justify-center py-6 pt-4">
              <p className="text-sm text-muted-foreground">
                SEO Prism v1.20.0
              </p>
            </CardFooter>
          </Card>
        </footer>
      </div>
    </div>
  )
}

export default App
