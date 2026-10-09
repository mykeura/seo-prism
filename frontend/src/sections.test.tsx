// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { describe, expect, it } from 'vitest'
import { SECTIONS, defaultSectionId, summarizeSections, worstSeverity } from './sections'
import { issue, scanResults } from './test/fixtures'

describe('worstSeverity', () => {
  it('returns the most serious severity present', () => {
    expect(worstSeverity([issue('a', 'low'), issue('b', 'high'), issue('c', 'medium')])).toBe('high')
    expect(worstSeverity([issue('a', 'info'), issue('b', 'low')])).toBe('low')
  })

  it('returns null when empty', () => {
    expect(worstSeverity([])).toBeNull()
  })
})

describe('summarizeSections', () => {
  it('has one summary per section, in order', () => {
    const summaries = summarizeSections(scanResults([]))
    expect(summaries.map((s) => s.id)).toEqual(SECTIONS.map((s) => s.id))
    expect(summaries.every((s) => s.count === 0 && s.worst === null)).toBe(true)
  })

  it('counts only issues that need attention, not info notices', () => {
    const results = scanResults([
      issue('robots_txt_found', 'info'),
      issue('missing_security_txt', 'info'),
      issue('missing_sitemap', 'medium'),
    ])
    const files = summarizeSections(results).find((s) => s.id === 'standardFiles')!
    expect(files.count).toBe(1)
    expect(files.worst).toBe('medium')
  })
})

describe('defaultSectionId', () => {
  it('opens the section with the most serious issue', () => {
    const results = scanResults([
      issue('broken_link', 'medium'),
      issue('missing_h1', 'high'),
      issue('missing_canonical', 'low'),
    ])
    expect(defaultSectionId(summarizeSections(results))).toBe('headerAnalysis')
  })

  it('breaks ties by report order', () => {
    const results = scanResults([issue('thin_content', 'medium'), issue('broken_link', 'medium')])
    expect(defaultSectionId(summarizeSections(results))).toBe('brokenLinks')
  })

  it('falls back to the first section when there is nothing to fix', () => {
    const results = scanResults([issue('robots_txt_found', 'info')])
    expect(defaultSectionId(summarizeSections(results))).toBe(SECTIONS[0].id)
  })
})
