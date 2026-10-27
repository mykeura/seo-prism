// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  API_KEY_REQUIRED_EVENT,
  apiFetch,
  clearApiKey,
  getApiKey,
  setApiKey,
} from './api'

beforeEach(() => {
  sessionStorage.clear()
  vi.unstubAllGlobals()
})

afterEach(() => {
  sessionStorage.clear()
  vi.unstubAllGlobals()
})

describe('API key storage', () => {
  it('stores a trimmed key and clears it', () => {
    setApiKey('  sekrit  ')
    expect(getApiKey()).toBe('sekrit')

    clearApiKey()
    expect(getApiKey()).toBe('')
  })
})

describe('apiFetch', () => {
  it('adds X-API-Key without dropping caller headers or body', async () => {
    setApiKey('sekrit')
    const fetchMock = vi.fn(
      async (_input: RequestInfo | URL, _init?: RequestInit) =>
        new Response('{}', { status: 200 }),
    )
    vi.stubGlobal('fetch', fetchMock)

    await apiFetch('http://api.example.com/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{"url":"https://example.com"}',
    })

    const init = fetchMock.mock.calls[0][1]!
    const headers = new Headers(init.headers)
    expect(headers.get('X-API-Key')).toBe('sekrit')
    expect(headers.get('Content-Type')).toBe('application/json')
    expect(init.body).toBe('{"url":"https://example.com"}')
  })

  it('does not send an empty API key header', async () => {
    const fetchMock = vi.fn(
      async (_input: RequestInfo | URL, _init?: RequestInit) =>
        new Response('{}', { status: 200 }),
    )
    vi.stubGlobal('fetch', fetchMock)

    await apiFetch('http://api.example.com/scans')

    const init = fetchMock.mock.calls[0][1]!
    expect(new Headers(init.headers).has('X-API-Key')).toBe(false)
  })

  it('notifies the UI when the API answers 401', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response(null, { status: 401 })))
    const listener = vi.fn()
    window.addEventListener(API_KEY_REQUIRED_EVENT, listener)

    try {
      await apiFetch('http://api.example.com/scans')
    } finally {
      window.removeEventListener(API_KEY_REQUIRED_EVENT, listener)
    }

    expect(listener).toHaveBeenCalledTimes(1)
  })
})
