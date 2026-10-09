// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { SECTIONS } from '../../sections'
import { issue, scanResults } from '../../test/fixtures'

const SEVERITIES = ['high', 'medium', 'low', 'info']
const TYPES = [
  'broken_link', 'broken_image', 'broken_script', 'broken_stylesheet',
  'missing_title', 'missing_description', 'duplicate_title', 'duplicate_description',
  'title_too_short', 'title_too_long', 'meta_description_too_short', 'meta_description_too_long',
  'missing_alt_text', 'short_alt_text',
  'missing_h1', 'multiple_h1_same_page', 'duplicate_h1', 'invalid_header_hierarchy',
  'robots_txt_found', 'missing_sitemap', 'missing_llms_txt',
  'meta_robots_noindex', 'meta_robots_nofollow',
  'hreflang_missing_self_reference', 'hreflang_invalid_code',
  'canonical_chain', 'canonical_to_404', 'canonical_to_redirect', 'canonical_url_variation',
  'missing_canonical', 'empty_canonical',
  'orphan_page', 'thin_content',
  'missing_structured_data', 'json_ld_invalid_json', 'microdata_unknown_type', 'rdfa_unknown_type',
]

describe('every section renders', () => {
  const results = scanResults(
    TYPES.map((type, index) =>
      issue(type, SEVERITIES[index % SEVERITIES.length], `https://example.com/${type}`),
    ),
  )
  const empty = scanResults([])

  it.each(SECTIONS.map((s) => s.id))('%s renders with issues of every kind', (id) => {
    const section = SECTIONS.find((s) => s.id === id)!
    const { container } = render(<>{section.render(results)}</>)
    expect(container.textContent?.length).toBeGreaterThan(20)
  })

  it.each(SECTIONS.map((s) => s.id))('%s renders its empty state', (id) => {
    const section = SECTIONS.find((s) => s.id === id)!
    const { container } = render(<>{section.render(empty)}</>)
    expect(container.textContent?.length).toBeGreaterThan(20)
  })
})
