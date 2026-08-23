import type { FormEvent } from 'react'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'

interface ScanFormProps {
  url: string
  onUrlChange: (url: string) => void
  onSubmit: (e: FormEvent) => void
  loading: boolean
  message: string | null
  error: string | null
}

export function ScanForm({ url, onUrlChange, onSubmit, loading, message, error }: ScanFormProps) {
  return (
    <>
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Start a New Scan</CardTitle>
          <CardDescription>
            Enter a URL to analyze for SEO issues
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="flex gap-4">
            <Input
              type="text"
              value={url}
              onChange={(e) => onUrlChange(e.target.value)}
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
    </>
  )
}
