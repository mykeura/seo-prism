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
            <Button type="submit" disabled={loading || !url.trim()} className="h-10 px-6">
              {loading ? 'Scanning...' : 'SCAN'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {message && (
        <div className="mb-6 rounded-lg border border-primary-400/20 bg-primary-500/10 px-4 py-3 text-sm text-primary-200">
          {message}
        </div>
      )}

      {error && (
        <div className="mb-6 rounded-lg border border-danger-400/25 bg-danger-500/10 px-4 py-3 text-sm text-danger-200">
          Error: {error}
        </div>
      )}
    </>
  )
}
