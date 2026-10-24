// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { useEffect, useState } from 'react'
import { useT } from '../i18n'
import type { ScanHistoryEntry, ScansResponse } from '../types_scans'

/** The API reports failures as {"detail": "..."}; surface it when present. */
export async function readErrorDetail(response: Response): Promise<string | null> {
  try {
    const body = await response.json()
    return typeof body?.detail === 'string' ? body.detail : null
  } catch {
    return null
  }
}

/**
 * Loads GET /scans once per panel open; scans is null while loading.
 * retry() re-runs the request against the same backend.
 */
export function useScanHistory(apiBaseUrl: string) {
  const t = useT()
  const [scans, setScans] = useState<ScanHistoryEntry[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let cancelled = false
    setScans(null)
    setError(null)

    ;(async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/scans`)
        if (!response.ok) {
          const detail = await readErrorDetail(response)
          throw new Error(detail ? `${t.history.loadFailed}: ${detail}` : t.history.loadFailed)
        }
        const data: ScansResponse = await response.json()
        if (!cancelled) setScans(data.scans ?? [])
      } catch (err) {
        if (cancelled) return
        if (err instanceof TypeError) {
          // fetch() rejects with TypeError when the server cannot be reached
          setError(t.app.backendUnreachable(apiBaseUrl))
        } else {
          setError(err instanceof Error ? err.message : t.app.genericError)
        }
      }
    })()

    return () => {
      cancelled = true
    }
  }, [apiBaseUrl, attempt, t])

  const retry = () => setAttempt((n) => n + 1)
  return { scans, error, retry }
}
