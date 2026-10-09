// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

// Hosts the backend treats as local (see backend/core/url_utils.is_local):
// they are served over plain http far more often than not.
const LOCAL_HOST = /^(localhost|127\.0\.0\.1|\[::1\]|[^/:]+\.(test|local)|192\.168\.[^/:]+|10\.[^/:]+)(:\d+)?(\/|$)/i

const HAS_SCHEME = /^[a-z][a-z0-9+.-]*:\/\//i

/**
 * Turn what people type ("example.com", "localhost:3000") into a URL the API
 * accepts. The backend only takes http(s) URLs with a host and answers
 * "Invalid URL format" otherwise.
 */
export function normalizeUrl(input: string): string {
  const value = input.trim()
  if (!value) return ''
  if (HAS_SCHEME.test(value)) return value
  return `${LOCAL_HOST.test(value) ? 'http' : 'https'}://${value}`
}
