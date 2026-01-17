import { useState } from 'react'
import { Button } from './components/ui/button'
import { Input } from './components/ui/input'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './components/ui/card'
import { Badge } from './components/ui/badge'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faLink,
  faFileAlt,
  faFileImage,
  faTag,
  faRobot,
  faShieldAlt,
  faMap,
  faFolder,
  faExclamationTriangle
} from '@fortawesome/free-solid-svg-icons'

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
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

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

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'destructive'
      case 'medium':
        return 'warning'
      case 'low':
        return 'secondary'
      case 'info':
        return 'default'
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
      case 'duplicate_title':
        return 'Duplicate Title'
      case 'duplicate_description':
        return 'Duplicate Description'
      case 'missing_alt_tag':
        return 'Missing Alt Tag'
      case 'missing_alt_text':
        return 'Missing Alt Text'
      case 'short_alt_text':
        return 'Short Alt Text'
      case 'missing_robots_txt':
        return 'Missing robots.txt'
      case 'missing_security_txt':
        return 'Missing security.txt'
      case 'missing_sitemap':
        return 'Missing Sitemap'
      case 'robots_txt_found':
        return 'robots.txt'
      case 'security_txt_found':
        return 'security.txt'
      case 'sitemap_found':
        return 'Sitemap'
      case 'missing_h1':
        return 'Missing H1 Header'
      case 'multiple_h1_same_page':
        return 'Multiple H1 Headers on Same Page'
      case 'duplicate_h1':
        return 'Duplicate H1 Header'
      case 'invalid_header_hierarchy':
        return 'Invalid Header Hierarchy'
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
        return <FontAwesomeIcon icon={faLink} className="text-destructive" />;
      case 'missing_title':
        return <FontAwesomeIcon icon={faFileAlt} className="text-primary-400" />;
      case 'missing_description':
        return <FontAwesomeIcon icon={faFileAlt} className="text-primary-400" />;
      case 'duplicate_title':
        return <FontAwesomeIcon icon={faFileAlt} className="text-warning" />;
      case 'duplicate_description':
        return <FontAwesomeIcon icon={faFileAlt} className="text-warning" />;
      case 'missing_alt_tag':
        return <FontAwesomeIcon icon={faFileImage} className="text-secondary" />;
      case 'missing_alt_text':
        return <FontAwesomeIcon icon={faFileImage} className="text-secondary" />;
      case 'short_alt_text':
        return <FontAwesomeIcon icon={faFileImage} className="text-secondary" />;
      case 'robots_txt_found':
        return <FontAwesomeIcon icon={faRobot} className="text-success" />;
      case 'security_txt_found':
        return <FontAwesomeIcon icon={faShieldAlt} className="text-success" />;
      case 'sitemap_found':
        return <FontAwesomeIcon icon={faMap} className="text-success" />;
      case 'missing_robots_txt':
        return <FontAwesomeIcon icon={faRobot} className="text-destructive" />;
      case 'missing_security_txt':
        return <FontAwesomeIcon icon={faShieldAlt} className="text-destructive" />;
      case 'missing_sitemap':
        return <FontAwesomeIcon icon={faMap} className="text-destructive" />;
      case 'missing_h1':
        return <FontAwesomeIcon icon={faTag} className="text-destructive" />;
      case 'multiple_h1_same_page':
        return <FontAwesomeIcon icon={faTag} className="text-destructive" />;
      case 'duplicate_h1':
        return <FontAwesomeIcon icon={faTag} className="text-warning" />;
      case 'invalid_header_hierarchy':
        return <FontAwesomeIcon icon={faTag} className="text-warning" />;
      default:
        return <FontAwesomeIcon icon={faExclamationTriangle} className="text-outline" />;
    }
  }

  const [activeTab, setActiveTab] = useState<'internal' | 'external'>('internal')
  const [metaTab, setMetaTab] = useState<'titles' | 'descriptions'>('titles')
  const [headerAnalysisTab, setHeaderAnalysisTab] = useState<'all' | 'hierarchy' | 'h1'>('all')
  const [showMoreBrokenLinks, setShowMoreBrokenLinks] = useState(5)
  const [showMoreMetaTags, setShowMoreMetaTags] = useState(5)
  const [showMoreImages, setShowMoreImages] = useState(5)
  const [showMoreH1, setShowMoreH1] = useState(5)
  const [showMoreHeaderHierarchy, setShowMoreHeaderHierarchy] = useState(5)
  const [showMoreHeaders, setShowMoreHeaders] = useState(5)
  const [showMoreStandardFiles, setShowMoreStandardFiles] = useState(5)

  const isInternalUrl = (url: string, baseUrl: string): boolean => {
    try {
      const urlObj = new URL(url)
      const baseUrlObj = new URL(baseUrl)
      return urlObj.hostname === baseUrlObj.hostname
    } catch {
      return false
    }
  }

  const renderResultsContent = (results: ScanResults, activeTab: 'internal' | 'external', setActiveTab: React.Dispatch<React.SetStateAction<'internal' | 'external'>>, metaTab: 'titles' | 'descriptions', setMetaTab: React.Dispatch<React.SetStateAction<'titles' | 'descriptions'>>, isInternalUrl: (url: string, baseUrl: string) => boolean, getIssueIcon: (type: string) => React.ReactNode, getIssueTypeLabel: (type: string) => string, getSeverityColor: (severity: string) => "destructive" | "warning" | "secondary" | "outline" | "default" | "success") => {
    
    // Helper function to render limited items with "Show More" option
    const renderLimitedItems = (items: any[], renderItem: (item: any) => React.ReactNode, showMoreState: number, setShowMoreState: React.Dispatch<React.SetStateAction<number>>) => {
      const visibleItems = items.slice(0, showMoreState);
      const hasMore = items.length > showMoreState;
      
      return (
        <div className="space-y-4">
          {visibleItems.map(renderItem)}
          {hasMore && (
            <div className="text-center mt-4">
              <button
                onClick={() => setShowMoreState(prev => prev + 10)}
                className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2 text-muted-foreground"
              >
                Showing {showMoreState} of {items.length} items.
              </button>
            </div>
          )}
        </div>
      );
    };
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

    const metaTagsIssues = results.issues.filter(issue =>
      issue.issue_type === 'missing_title' ||
      issue.issue_type === 'missing_description' ||
      issue.issue_type === 'duplicate_title' ||
      issue.issue_type === 'duplicate_description'
    )

    const missingTitles = metaTagsIssues.filter(issue =>
      issue.issue_type === 'missing_title' ||
      issue.issue_type === 'duplicate_title'
    )

    const missingDescriptions = metaTagsIssues.filter(issue =>
      issue.issue_type === 'missing_description' ||
      issue.issue_type === 'duplicate_description'
    )

    const standardFilesIssues = results.issues.filter(issue =>
      issue.issue_type === 'robots_txt_found' ||
      issue.issue_type === 'security_txt_found' ||
      issue.issue_type === 'sitemap_found' ||
      issue.issue_type === 'missing_robots_txt' ||
      issue.issue_type === 'missing_security_txt' ||
      issue.issue_type === 'missing_sitemap'
    )


    const missingAltTagIssues = results.issues.filter(issue =>
      issue.issue_type === 'missing_alt_tag' ||
      issue.issue_type === 'missing_alt_text' ||
      issue.issue_type === 'short_alt_text'
    )

    const h1Issues = results.issues.filter(issue =>
      issue.issue_type === 'missing_h1' ||
      issue.issue_type === 'multiple_h1_same_page' ||
      issue.issue_type === 'duplicate_h1'
    )

    const headerHierarchyIssues = results.issues.filter(issue =>
      issue.issue_type === 'invalid_header_hierarchy'
    )

    const headerIssues = results.issues.filter(issue =>
      issue.issue_type === 'missing_h1' ||
      issue.issue_type === 'multiple_h1_same_page' ||
      issue.issue_type === 'duplicate_h1' ||
      issue.issue_type === 'invalid_header_hierarchy'
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
            <Card>
              <CardHeader>
                <CardTitle>Broken Links</CardTitle>
                <CardDescription>
                  {brokenLinkIssues.length} broken link{brokenLinkIssues.length !== 1 ? 's' : ''} detected
                </CardDescription>
              </CardHeader>
              <CardContent>
                {brokenLinkIssues.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4"><FontAwesomeIcon icon={faLink} className="text-primary-400" /></div>
                    <h3 className="text-xl font-semibold text-emerald-400 mb-2">No Broken Links Found!</h3>
                    <p className="text-muted-foreground">All internal and external links are working correctly.</p>
                  </div>
                ) : (
                  <>
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

                    {renderLimitedItems(
                      (activeTab === 'internal' ? internalLinks : externalLinks),
                      (issue: any) => (
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
                      ),
                      showMoreBrokenLinks,
                      setShowMoreBrokenLinks
                    )}
                    {(activeTab === 'internal' ? internalLinks : externalLinks).length === 0 && (
                      <div className="text-center py-8 text-muted-foreground">
                        No {activeTab === 'internal' ? 'internal' : 'external'} broken links found
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Meta Tags Issues</CardTitle>
                <CardDescription>
                  {metaTagsIssues.length} meta tag issue{metaTagsIssues.length !== 1 ? 's' : ''} detected
                </CardDescription>
              </CardHeader>
              <CardContent>
                {metaTagsIssues.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4"><FontAwesomeIcon icon={faFileAlt} className="text-primary-400" /></div>
                    <h3 className="text-xl font-semibold text-emerald-400 mb-2">No Meta Tag Issues Found!</h3>
                    <p className="text-muted-foreground">All pages have proper title tags and descriptions.</p>
                  </div>
                ) : (
                  <>
                    <div className="flex gap-2 mb-4 border-b border-border">
                      <button
                        onClick={() => setMetaTab('titles')}
                        className={`px-4 py-2 font-medium transition-colors ${
                          metaTab === 'titles'
                            ? 'text-primary-400 border-b-2 border-primary-400'
                            : 'text-muted-foreground hover:text-foreground'
                        }`}
                      >
                        Missing Titles ({missingTitles.length})
                      </button>
                      <button
                        onClick={() => setMetaTab('descriptions')}
                        className={`px-4 py-2 font-medium transition-colors ${
                          metaTab === 'descriptions'
                            ? 'text-primary-400 border-b-2 border-primary-400'
                            : 'text-muted-foreground hover:text-foreground'
                        }`}
                      >
                        Missing Descriptions ({missingDescriptions.length})
                      </button>
                    </div>

                    {renderLimitedItems(
                      (metaTab === 'titles' ? missingTitles : missingDescriptions),
                      (issue: any) => (
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
                            {issue.description && (
                              <div className="text-sm text-muted-foreground">{issue.description}</div>
                            )}
                          </div>
                        </div>
                      ),
                      showMoreMetaTags,
                      setShowMoreMetaTags
                    )}
                    {(metaTab === 'titles' ? missingTitles : missingDescriptions).length === 0 && (
                      <div className="text-center py-8 text-muted-foreground">
                        No {metaTab === 'titles' ? 'missing titles' : 'missing descriptions'} found
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>


            <Card>
              <CardHeader>
                <CardTitle>Images Without Alt</CardTitle>
                <CardDescription>
                  {missingAltTagIssues.length} image{missingAltTagIssues.length !== 1 ? 's' : ''} missing alt tag{missingAltTagIssues.length !== 1 ? 's' : ''}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {missingAltTagIssues.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4"><FontAwesomeIcon icon={faFileImage} className="text-primary-400" /></div>
                    <h3 className="text-xl font-semibold text-emerald-400 mb-2">All Images Have Alt Tags!</h3>
                    <p className="text-muted-foreground">All images have proper alt tags for SEO and accessibility.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {missingAltTagIssues.slice(0, showMoreImages).map((issue) => (
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
                            <span className="text-sm text-muted-foreground">Image URL:</span>
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
                              <span className="text-sm text-muted-foreground">Found on page:</span>
                              <a
                                href={issue.source_page}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="ml-2 text-sm text-primary-400 hover:underline break-all"
                              >
                                {issue.source_page}
                              </a>
                            </div>
                          )}
                          {issue.description && (
                            <div className="text-sm text-muted-foreground">{issue.description}</div>
                          )}
                        </div>
                      </div>
                    ))}
                    {missingAltTagIssues.length > showMoreImages && (
                      <div className="text-center mt-4">
                        <button
                          onClick={() => setShowMoreImages(prev => prev + 10)}
                          className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2 text-muted-foreground"
                        >
                          Showing {showMoreImages} of {missingAltTagIssues.length} items.
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Headers Analysis Section with Tabs */}
            <Card>
              <CardHeader>
                <CardTitle>Header Analysis</CardTitle>
                <CardDescription>
                  Comprehensive header analysis showing all header-related issues
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2 mb-4 border-b border-border">
                  <button
                    onClick={() => setHeaderAnalysisTab('all')}
                    className={`px-4 py-2 font-medium transition-colors ${
                      headerAnalysisTab === 'all'
                        ? 'text-primary-400 border-b-2 border-primary-400'
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    All Headers ({headerIssues.length})
                  </button>
                  <button
                    onClick={() => setHeaderAnalysisTab('hierarchy')}
                    className={`px-4 py-2 font-medium transition-colors ${
                      headerAnalysisTab === 'hierarchy'
                        ? 'text-primary-400 border-b-2 border-primary-400'
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    Hierarchy Issues ({headerHierarchyIssues.length})
                  </button>
                  <button
                    onClick={() => setHeaderAnalysisTab('h1')}
                    className={`px-4 py-2 font-medium transition-colors ${
                      headerAnalysisTab === 'h1'
                        ? 'text-primary-400 border-b-2 border-primary-400'
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    H1 Issues ({h1Issues.length})
                  </button>
                </div>

                {headerIssues.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4"><FontAwesomeIcon icon={faTag} className="text-primary-400" /></div>
                    <h3 className="text-xl font-semibold text-emerald-400 mb-2">No Header Issues Found!</h3>
                    <p className="text-muted-foreground">All pages have proper header structure.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {renderLimitedItems(
                      (headerAnalysisTab === 'all' ? headerIssues :
                       headerAnalysisTab === 'hierarchy' ? headerHierarchyIssues :
                       h1Issues),
                      (issue: any) => (
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
                            {issue.source_page && issue.source_page !== issue.url && (
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
                      ),
                      (headerAnalysisTab === 'all' ? showMoreHeaders :
                       headerAnalysisTab === 'hierarchy' ? showMoreHeaderHierarchy :
                       showMoreH1),
                      (headerAnalysisTab === 'all' ? setShowMoreHeaders :
                       headerAnalysisTab === 'hierarchy' ? setShowMoreHeaderHierarchy :
                       setShowMoreH1)
                    )}
                    {(headerAnalysisTab === 'all' ? headerIssues :
                     headerAnalysisTab === 'hierarchy' ? headerHierarchyIssues :
                     h1Issues).length === 0 && (
                      <div className="text-center py-8 text-muted-foreground">
                        No {headerAnalysisTab === 'all' ? 'header' :
                             headerAnalysisTab === 'hierarchy' ? 'hierarchy' : 'H1'} issues found
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Standard Files</CardTitle>
                <CardDescription>
                  {standardFilesIssues.length} standard file{standardFilesIssues.length !== 1 ? 's' : ''} found
                </CardDescription>
              </CardHeader>
              <CardContent>
                {standardFilesIssues.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4"><FontAwesomeIcon icon={faFolder} className="text-primary-400" /></div>
                    <h3 className="text-xl font-semibold text-muted-foreground mb-2">No Standard Files Found</h3>
                    <p className="text-muted-foreground">No robots.txt, security.txt or sitemap files were detected.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {standardFilesIssues.slice(0, showMoreStandardFiles).map((issue) => (
                      <div
                        key={issue.id}
                        className="p-4 rounded-lg border border-border bg-emerald-600/5 hover:bg-emerald-600/10 transition-colors"
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
                          {issue.description && (
                            <div className="text-sm text-muted-foreground">{issue.description}</div>
                          )}
                        </div>
                      </div>
                    ))}
                    {standardFilesIssues.length > showMoreStandardFiles && (
                      <div className="text-center mt-4">
                        <button
                          onClick={() => setShowMoreStandardFiles(prev => prev + 10)}
                          className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2 text-muted-foreground"
                        >
                          Showing {showMoreStandardFiles} of {standardFilesIssues.length} items.
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </>
    )
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <header className="mb-12 text-center">
          <h1 className="text-4xl font-bold mb-2 bg-linear-to-r from-primary-400 via-secondary-500 to-accent-500 bg-clip-text text-transparent">
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

            {renderResultsContent(results, activeTab, setActiveTab, metaTab, setMetaTab, isInternalUrl, getIssueIcon, getIssueTypeLabel, getSeverityColor)}
          </div>
        )}
        
        <footer className="mt-12 text-center">
          <Card>
            <CardFooter className="justify-center py-6 pt-4">
              <p className="text-sm text-muted-foreground">
                Todos los derechos reservados © 2026 Intellectus Labs
              </p>
            </CardFooter>
          </Card>
        </footer>
      </div>
    </div>
  )
}

export default App