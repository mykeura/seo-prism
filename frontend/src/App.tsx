import { useState } from 'react'
import { Button } from './components/ui/button'
import { Input } from './components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card'
import { Badge } from './components/ui/badge'

interface Issue {
  id: number
  issue_type: string
  url: string
  source_page?: string
  description?: string
  severity: string
}

interface ScanResults {
  scan: {
    id: number
    url: string
    timestamp: string
    total_pages: number
    total_issues: number
  }
  issues: Issue[]
  pages: any[]
}

function App() {
  const [results, setResults] = useState<ScanResults | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [url, setUrl] = useState('')

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setError(null)
    setMessage(null)
    setResults(null)

    try {
      const scanResponse = await fetch('http://localhost:8000/scan', {
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

      const resultsResponse = await fetch('http://localhost:8000/results')
      
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

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'destructive'
      case 'medium':
        return 'warning'
      case 'low':
        return 'secondary'
      default:
        return 'outline'
    }
  }

  const getIssueTypeLabel = (type: string) => {
    switch (type) {
      case 'broken_link':
        return 'Broken Link'
      case 'broken_image':
        return 'Broken Image'
      case 'broken_script':
        return 'Broken Script'
      case 'broken_stylesheet':
        return 'Broken Stylesheet'
      case 'broken_resource':
        return 'Broken Resource'
      case 'missing_title':
        return 'Missing Title'
      case 'missing_description':
        return 'Missing Description'
      default:
        return type
    }
  }

  const getIssueIcon = (type: string) => {
    switch (type) {
      case 'broken_link':
      case 'broken_image':
      case 'broken_script':
      case 'broken_stylesheet':
      case 'broken_resource':
        return '🔗'
      case 'missing_title':
        return '📝'
      case 'missing_description':
        return '📄'
      default:
        return '⚠️'
    }
  }

  const [activeTab, setActiveTab] = useState<'internal' | 'external'>('internal')

  const isInternalUrl = (url: string, baseUrl: string): boolean => {
    try {
      const urlObj = new URL(url)
      const baseUrlObj = new URL(baseUrl)
      return urlObj.hostname === baseUrlObj.hostname
    } catch {
      return false
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <header className="mb-12 text-center">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary-400 via-secondary-500 to-accent-500 bg-clip-text text-transparent">
            SEO Prism
          </h1>
          <p className="text-muted-foreground text-lg">
            Detect broken links and missing meta-tags
          </p>
        </header>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Start a New Scan</CardTitle>
            <CardDescription>
              Enter a URL to analyze for SEO issues
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleScan} className="flex gap-4">
              <Input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter URL (e.g., http://localhost:3000)"
                disabled={loading}
                className="flex-1"
              />
              <Button type="submit" disabled={loading || !url.trim()}>
                {loading ? 'Scanning...' : 'SCAN'}
              </Button>
            </form>
          </CardContent>
        </Card>

        {message && (
          <div className="mb-6 p-4 rounded-lg bg-primary-600/10 border border-primary-600/20 text-primary-400">
            {message}
          </div>
        )}
        
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-600/10 border border-red-600/20 text-red-400">
            Error: {error}
          </div>
        )}
        
        {results && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Scan Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="p-4 rounded-lg bg-secondary-600/10 border border-secondary-600/20">
                    <div className="text-sm text-muted-foreground mb-1">URL</div>
                    <div className="font-semibold text-sm truncate">{results.scan.url}</div>
                  </div>
                  <div className="p-4 rounded-lg bg-secondary-600/10 border border-secondary-600/20">
                    <div className="text-sm text-muted-foreground mb-1">Pages Analyzed</div>
                    <div className="text-2xl font-bold text-primary-400">{results.scan.total_pages}</div>
                  </div>
                  <div className="p-4 rounded-lg bg-secondary-600/10 border border-secondary-600/20">
                    <div className="text-sm text-muted-foreground mb-1">Total Issues</div>
                    <div className={`text-2xl font-bold ${results.scan.total_issues === 0 ? "text-emerald-400" : "text-accent-400"}`}>{results.scan.total_issues}</div>
                  </div>
                  <div className="p-4 rounded-lg bg-secondary-600/10 border border-secondary-600/20">
                    <div className="text-sm text-muted-foreground mb-1">Scan Time</div>
                    <div className="text-sm font-semibold">{new Date(results.scan.timestamp).toLocaleString()}</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {(() => {
              const brokenLinkIssues = results.issues.filter(issue =>
                issue.issue_type === 'broken_link' ||
                issue.issue_type === 'broken_image' ||
                issue.issue_type === 'broken_script' ||
                issue.issue_type === 'broken_stylesheet' ||
                issue.issue_type === 'broken_resource'
              )

              const internalLinks = brokenLinkIssues.filter(issue =>
                isInternalUrl(issue.url, results.scan.url)
              )

              const externalLinks = brokenLinkIssues.filter(issue =>
                !isInternalUrl(issue.url, results.scan.url)
              )

              const otherIssues = results.issues.filter(issue =>
                issue.issue_type !== 'broken_link' &&
                issue.issue_type !== 'broken_image' &&
                issue.issue_type !== 'broken_script' &&
                issue.issue_type !== 'broken_stylesheet' &&
                issue.issue_type !== 'broken_resource'
              )

              return (
                <>
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
                      {brokenLinkIssues.length > 0 && (
                        <Card>
                          <CardHeader>
                            <CardTitle>Broken Links</CardTitle>
                            <CardDescription>
                              {brokenLinkIssues.length} broken link{brokenLinkIssues.length !== 1 ? 's' : ''} detected
                            </CardDescription>
                          </CardHeader>
                          <CardContent>
                            <div className="flex gap-2 mb-4 border-b border-border">
                              <button
                                onClick={() => setActiveTab('internal')}
                                className={`px-4 py-2 font-medium transition-colors ${
                                  activeTab === 'internal'
                                    ? 'text-primary-400 border-b-2 border-primary-400'
                                    : 'text-muted-foreground hover:text-foreground'
                                }`}
                              >
                                Internal Links ({internalLinks.length})
                              </button>
                              <button
                                onClick={() => setActiveTab('external')}
                                className={`px-4 py-2 font-medium transition-colors ${
                                  activeTab === 'external'
                                    ? 'text-primary-400 border-b-2 border-primary-400'
                                    : 'text-muted-foreground hover:text-foreground'
                                }`}
                              >
                                External Links ({externalLinks.length})
                              </button>
                            </div>

                            <div className="space-y-4">
                              {(activeTab === 'internal' ? internalLinks : externalLinks).map((issue) => (
                                <div
                                  key={issue.id}
                                  className="p-4 rounded-lg border border-border bg-secondary-600/5 hover:bg-secondary-600/10 transition-colors"
                                >
                                  <div className="flex items-start justify-between gap-4 mb-2">
                                    <div className="flex items-center gap-2">
                                      <span className="text-xl">{getIssueIcon(issue.issue_type)}</span>
                                      <span className="font-semibold">{getIssueTypeLabel(issue.issue_type)}</span>
                                    </div>
                                    <Badge variant={getSeverityColor(issue.severity)}>
                                      {issue.severity.toUpperCase()}
                                    </Badge>
                                  </div>
                                  <div className="space-y-2">
                                    <div>
                                      <span className="text-sm text-muted-foreground">URL:</span>
                                      <a
                                        href={issue.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="ml-2 text-sm text-primary-400 hover:underline break-all"
                                      >
                                        {issue.url}
                                      </a>
                                    </div>
                                    {issue.source_page && (
                                      <div>
                                        <span className="text-sm text-muted-foreground">Source:</span>
                                        <span className="ml-2 text-sm break-all">{issue.source_page}</span>
                                      </div>
                                    )}
                                    {issue.description && (
                                      <div className="text-sm text-muted-foreground">{issue.description}</div>
                                    )}
                                  </div>
                                </div>
                              ))}
                              {(activeTab === 'internal' ? internalLinks : externalLinks).length === 0 && (
                                <div className="text-center py-8 text-muted-foreground">
                                  No {activeTab === 'internal' ? 'internal' : 'external'} broken links found
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      )}

                      {otherIssues.length > 0 && (
                        <Card>
                          <CardHeader>
                            <CardTitle>Other Issues</CardTitle>
                            <CardDescription>
                              {otherIssues.length} other issue{otherIssues.length !== 1 ? 's' : ''} detected
                            </CardDescription>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-4">
                              {otherIssues.map((issue) => (
                                <div
                                  key={issue.id}
                                  className="p-4 rounded-lg border border-border bg-secondary-600/5 hover:bg-secondary-600/10 transition-colors"
                                >
                                  <div className="flex items-start justify-between gap-4 mb-2">
                                    <div className="flex items-center gap-2">
                                      <span className="text-xl">{getIssueIcon(issue.issue_type)}</span>
                                      <span className="font-semibold">{getIssueTypeLabel(issue.issue_type)}</span>
                                    </div>
                                    <Badge variant={getSeverityColor(issue.severity)}>
                                      {issue.severity.toUpperCase()}
                                    </Badge>
                                  </div>
                                  <div className="space-y-2">
                                    <div>
                                      <span className="text-sm text-muted-foreground">URL:</span>
                                      <a
                                        href={issue.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="ml-2 text-sm text-primary-400 hover:underline break-all"
                                      >
                                        {issue.url}
                                      </a>
                                    </div>
                                    {issue.source_page && (
                                      <div>
                                        <span className="text-sm text-muted-foreground">Source:</span>
                                        <span className="ml-2 text-sm break-all">{issue.source_page}</span>
                                      </div>
                                    )}
                                    {issue.description && (
                                      <div className="text-sm text-muted-foreground">{issue.description}</div>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </CardContent>
                        </Card>
                      )}
                    </>
                  )}
                </>
              )
            })()}
          </div>
        )}
      </div>
    </div>
  )
}

export default App