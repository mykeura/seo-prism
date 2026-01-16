import { useState } from 'react'

interface UrlInputProps {
  onScan: (url: string) => void
  loading: boolean
}

function UrlInput({ onScan, loading }: UrlInputProps) {
  const [url, setUrl] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (url.trim()) {
      onScan(url.trim())
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '30px' }}>
      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter URL (e.g., http://localhost:3000)"
          disabled={loading}
          style={{
            flex: 1,
            padding: '12px',
            fontSize: '16px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            minWidth: '300px'
          }}
        />
        <button
          type="submit"
          disabled={loading || !url.trim()}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            backgroundColor: loading ? '#ccc' : '#2196f3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 'bold'
          }}
        >
          {loading ? 'Scanning...' : 'SCAN'}
        </button>
      </div>
    </form>
  )
}

export default UrlInput