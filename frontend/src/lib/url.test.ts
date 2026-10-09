// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { describe, expect, it } from 'vitest'
import { normalizeUrl } from './url'

describe('normalizeUrl', () => {
  it('adds https to a bare domain', () => {
    expect(normalizeUrl('example.com')).toBe('https://example.com')
    expect(normalizeUrl('  www.example.com/blog  ')).toBe('https://www.example.com/blog')
  })

  it('uses http for hosts the backend treats as local', () => {
    expect(normalizeUrl('localhost:3000')).toBe('http://localhost:3000')
    expect(normalizeUrl('127.0.0.1:8080/app')).toBe('http://127.0.0.1:8080/app')
    expect(normalizeUrl('mysite.test')).toBe('http://mysite.test')
    expect(normalizeUrl('shop.local/path')).toBe('http://shop.local/path')
    expect(normalizeUrl('192.168.1.20')).toBe('http://192.168.1.20')
    expect(normalizeUrl('10.0.0.5:5000')).toBe('http://10.0.0.5:5000')
  })

  it('does not treat look-alike public domains as local', () => {
    expect(normalizeUrl('localhost.example.com')).toBe('https://localhost.example.com')
    expect(normalizeUrl('mytest.com')).toBe('https://mytest.com')
  })

  it('leaves URLs that already have a scheme untouched', () => {
    expect(normalizeUrl('http://example.com')).toBe('http://example.com')
    expect(normalizeUrl('HTTPS://Example.com/x')).toBe('HTTPS://Example.com/x')
    // an unsupported scheme is passed through so the API can reject it with a clear message
    expect(normalizeUrl('ftp://example.com')).toBe('ftp://example.com')
  })

  it('returns an empty string for blank input', () => {
    expect(normalizeUrl('')).toBe('')
    expect(normalizeUrl('   ')).toBe('')
  })
})
