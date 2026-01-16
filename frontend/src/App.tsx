import { useState } from 'react'
import UrlInput from './components/UrlInput'
import ResultsTable from './components/ResultsTable'

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

  const handleScan = async (url: string) => {
    setLoading(true)
    setError(null)
    setMessage(null)
    setResults(null)

    try {
      // Start scan
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

      // Get results
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

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '40px' }}>SEO Prism</h1>
      
      <UrlInput onScan={handleScan} loading={loading} />
      
      {message && (
        <div style={{
          padding: '10px',
          margin: '20px 0',
          backgroundColor: '#e3f2fd',
          borderRadius: '4px',
          border: '1px solid #2196f3'
        }}>
          {message}
        </div>
      )}
      
      {error && (
        <div style={{
          padding: '10px',
          margin: '20px 0',
          backgroundColor: '#ffebee',
          borderRadius: '4px',
          border: '1px solid #f44336',
          color: '#c62828'
        }}>
          Error: {error}
        </div>
      )}
      
      {results && <ResultsTable results={results} />}
    </div>
  )
}

export default App