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
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <header className="mb-12 text-center">
          <h1 className="text-4xl font-bold mb-2 bg-linear-to-r from-primary-400 via-secondary-500 to-accent-500 bg-clip-text text-transparent">
            SEO Prism
          </h1>
          <p className="text-muted-foreground text-lg">
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
              <Card className="border-emerald-600/20 bg-emerald-600/5">
                <CardContent className="pt-6">
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4">✅</div>
                    <h3 className="text-xl font-semibold text-emerald-400 mb-2">No Issues Found!</h3>
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
          <Card>
            <CardFooter className="justify-center py-6 pt-4">
              <p className="text-sm text-muted-foreground">
                All rights reserved © 2026 <a href="https://paracaidas.digital/" target="_blank" rel="noopener noreferrer" className="text-primary-400 hover:underline">Paracaídas Digital</a> · SEO Prism v1.19.1
              </p>
            </CardFooter>
          </Card>
        </footer>
      </div>
    </div>
  )
}

export default App
