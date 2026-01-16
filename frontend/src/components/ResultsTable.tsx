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

interface ResultsTableProps {
  results: ScanResults
}

function ResultsTable({ results }: ResultsTableProps) {
  const { scan, issues } = results

  // Group issues by type
  const brokenLinks = issues.filter(i => i.issue_type === 'broken_link')
  const brokenImages = issues.filter(i => i.issue_type === 'broken_image')
  const brokenScripts = issues.filter(i => i.issue_type === 'broken_script')
  const brokenStylesheets = issues.filter(i => i.issue_type === 'broken_stylesheet')
  const brokenResources = issues.filter(i => i.issue_type === 'broken_resource')
  const missingTitles = issues.filter(i => i.issue_type === 'missing_title')
  const missingDescriptions = issues.filter(i => i.issue_type === 'missing_description')

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return '#f44336'
      case 'medium':
        return '#ff9800'
      case 'low':
        return '#4caf50'
      default:
        return '#9e9e9e'
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

  return (
    <div>
      <div style={{
        marginBottom: '20px',
        padding: '20px',
        backgroundColor: '#f5f5f5',
        borderRadius: '4px',
        border: '1px solid #ddd'
      }}>
        <h3 style={{ marginTop: 0 }}>Scan Summary</h3>
        <p><strong>URL:</strong> {scan.url}</p>
        <p><strong>Pages Analyzed:</strong> {scan.total_pages}</p>
        <p><strong>Total Issues:</strong> {scan.total_issues}</p>
        <p><strong>Scan Time:</strong> {new Date(scan.timestamp).toLocaleString()}</p>
      </div>

      {issues.length === 0 ? (
        <div style={{
          padding: '20px',
          backgroundColor: '#e8f5e9',
          borderRadius: '4px',
          border: '1px solid #4caf50',
          textAlign: 'center'
        }}>
          <h3 style={{ color: '#2e7d32', marginTop: 0 }}>✅ No Issues Found!</h3>
          <p>Your website looks great!</p>
        </div>
      ) : (
        <>
          {brokenLinks.length > 0 && (
            <div style={{ marginBottom: '30px' }}>
              <h3 style={{ marginTop: 0 }}>🔗 Broken Links ({brokenLinks.length})</h3>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                backgroundColor: 'white',
                border: '1px solid #ddd'
              }}>
                <thead>
                  <tr style={{ backgroundColor: '#f5f5f5' }}>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Broken Link</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Source Page</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Type</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {brokenLinks.map((issue) => (
                    <tr key={issue.id}>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        <a href={issue.url} target="_blank" rel="noopener noreferrer" style={{ color: '#2196f3' }}>
                          {issue.url}
                        </a>
                      </td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>{issue.source_page}</td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>{getIssueTypeLabel(issue.issue_type)}</td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: getSeverityColor(issue.severity),
                          color: 'white',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }}>
                          {issue.severity.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {brokenImages.length > 0 && (
            <div style={{ marginBottom: '30px' }}>
              <h3 style={{ marginTop: 0 }}>🖼️ Broken Images ({brokenImages.length})</h3>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                backgroundColor: 'white',
                border: '1px solid #ddd'
              }}>
                <thead>
                  <tr style={{ backgroundColor: '#f5f5f5' }}>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Broken Image</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Source Page</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Type</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {brokenImages.map((issue) => (
                    <tr key={issue.id}>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        <a href={issue.url} target="_blank" rel="noopener noreferrer" style={{ color: '#2196f3' }}>
                          {issue.url}
                        </a>
                      </td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>{issue.source_page}</td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>{getIssueTypeLabel(issue.issue_type)}</td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: getSeverityColor(issue.severity),
                          color: 'white',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }}>
                          {issue.severity.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {brokenScripts.length > 0 && (
            <div style={{ marginBottom: '30px' }}>
              <h3 style={{ marginTop: 0 }}>⚙️ Broken Scripts ({brokenScripts.length})</h3>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                backgroundColor: 'white',
                border: '1px solid #ddd'
              }}>
                <thead>
                  <tr style={{ backgroundColor: '#f5f5f5' }}>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Broken Script</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Source Page</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Type</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {brokenScripts.map((issue) => (
                    <tr key={issue.id}>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        <a href={issue.url} target="_blank" rel="noopener noreferrer" style={{ color: '#2196f3' }}>
                          {issue.url}
                        </a>
                      </td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>{issue.source_page}</td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>{getIssueTypeLabel(issue.issue_type)}</td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: getSeverityColor(issue.severity),
                          color: 'white',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }}>
                          {issue.severity.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {brokenStylesheets.length > 0 && (
            <div style={{ marginBottom: '30px' }}>
              <h3 style={{ marginTop: 0 }}>🎨 Broken Stylesheets ({brokenStylesheets.length})</h3>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                backgroundColor: 'white',
                border: '1px solid #ddd'
              }}>
                <thead>
                  <tr style={{ backgroundColor: '#f5f5f5' }}>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Broken Stylesheet</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Source Page</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Type</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {brokenStylesheets.map((issue) => (
                    <tr key={issue.id}>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        <a href={issue.url} target="_blank" rel="noopener noreferrer" style={{ color: '#2196f3' }}>
                          {issue.url}
                        </a>
                      </td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>{issue.source_page}</td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>{getIssueTypeLabel(issue.issue_type)}</td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: getSeverityColor(issue.severity),
                          color: 'white',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }}>
                          {issue.severity.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {brokenResources.length > 0 && (
            <div style={{ marginBottom: '30px' }}>
              <h3 style={{ marginTop: 0 }}>📦 Broken Resources ({brokenResources.length})</h3>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                backgroundColor: 'white',
                border: '1px solid #ddd'
              }}>
                <thead>
                  <tr style={{ backgroundColor: '#f5f5f5' }}>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Broken Resource</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Source Page</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Type</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {brokenResources.map((issue) => (
                    <tr key={issue.id}>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        <a href={issue.url} target="_blank" rel="noopener noreferrer" style={{ color: '#2196f3' }}>
                          {issue.url}
                        </a>
                      </td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>{issue.source_page}</td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>{getIssueTypeLabel(issue.issue_type)}</td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: getSeverityColor(issue.severity),
                          color: 'white',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }}>
                          {issue.severity.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {missingTitles.length > 0 && (
            <div style={{ marginBottom: '30px' }}>
              <h3 style={{ marginTop: 0 }}>📝 Missing Titles ({missingTitles.length})</h3>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                backgroundColor: 'white',
                border: '1px solid #ddd'
              }}>
                <thead>
                  <tr style={{ backgroundColor: '#f5f5f5' }}>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Page URL</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Type</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {missingTitles.map((issue) => (
                    <tr key={issue.id}>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        <a href={issue.url} target="_blank" rel="noopener noreferrer" style={{ color: '#2196f3' }}>
                          {issue.url}
                        </a>
                      </td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>{getIssueTypeLabel(issue.issue_type)}</td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: getSeverityColor(issue.severity),
                          color: 'white',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }}>
                          {issue.severity.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {missingDescriptions.length > 0 && (
            <div style={{ marginBottom: '30px' }}>
              <h3 style={{ marginTop: 0 }}>📄 Missing Descriptions ({missingDescriptions.length})</h3>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                backgroundColor: 'white',
                border: '1px solid #ddd'
              }}>
                <thead>
                  <tr style={{ backgroundColor: '#f5f5f5' }}>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Page URL</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Type</th>
                    <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {missingDescriptions.map((issue) => (
                    <tr key={issue.id}>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        <a href={issue.url} target="_blank" rel="noopener noreferrer" style={{ color: '#2196f3' }}>
                          {issue.url}
                        </a>
                      </td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>{getIssueTypeLabel(issue.issue_type)}</td>
                      <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: getSeverityColor(issue.severity),
                          color: 'white',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }}>
                          {issue.severity.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default ResultsTable