// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

const API_KEY_STORAGE = 'seo-prism.api-key'

/** Dispatched on any 401 so the header can reveal the API-key field. */
export const API_KEY_REQUIRED_EVENT = 'seo-prism:api-key-required'

function storage(): Storage | null {
  try {
    return typeof sessionStorage !== 'undefined' ? sessionStorage : null
  } catch {
    return null
  }
}

export function getApiKey(): string {
  return storage()?.getItem(API_KEY_STORAGE) ?? ''
}

export function setApiKey(key: string): void {
  const store = storage()
  if (!store) return
  const trimmed = key.trim()
  if (trimmed) store.setItem(API_KEY_STORAGE, trimmed)
  else store.removeItem(API_KEY_STORAGE)
}

export function clearApiKey(): void {
  storage()?.removeItem(API_KEY_STORAGE)
}

/**
 * fetch() wrapper: adds the X-API-Key header when the operator configured
 * one, and surfaces 401s to the API-key control. The key lives only in
 * sessionStorage and is never part of the bundle.
 */
export async function apiFetch(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Response> {
  const headers = new Headers(init?.headers)
  const key = getApiKey()
  if (key) headers.set('X-API-Key', key)

  const response = await fetch(input, { ...init, headers })
  if (response.status === 401 && typeof window !== 'undefined') {
    window.dispatchEvent(new Event(API_KEY_REQUIRED_EVENT))
  }
  return response
}
