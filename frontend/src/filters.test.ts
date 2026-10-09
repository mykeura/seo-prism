// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

/// <reference types="node" />
import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { SECTIONS } from './sections'
import { issue, scanResults } from './test/fixtures'
import { getCanonicalIssues, getMissingCanonical, getStructuredDataIssues } from './filters'

// Issue types the backend can emit. When the backend sources are next to the
// frontend (this repository) they are read from the Python modules, so a new
// type added there without a section here fails this test. The static list
// is the fallback and a floor.
const STATIC_BACKEND_TYPES = [
  'broken_link', 'broken_image', 'broken_script', 'broken_stylesheet', 'broken_resource',
  'missing_title', 'missing_description', 'duplicate_title', 'duplicate_description',
  'title_too_short', 'title_too_long', 'meta_description_too_short', 'meta_description_too_long',
  'missing_alt_text', 'short_alt_text',
  'missing_h1', 'multiple_h1_same_page', 'duplicate_h1', 'invalid_header_hierarchy',
  'robots_txt_found', 'security_txt_found', 'sitemap_found', 'llms_txt_found',
  'missing_robots_txt', 'missing_security_txt', 'missing_sitemap', 'missing_llms_txt',
  'meta_robots_noindex', 'meta_robots_nofollow',
  'hreflang_missing_self_reference', 'hreflang_missing_x_default', 'hreflang_duplicate_code',
  'hreflang_invalid_code', 'hreflang_missing_return_link', 'hreflang_missing_canonical',
  'canonical_chain', 'canonical_to_404', 'canonical_to_redirect', 'canonical_url_variation',
  'missing_canonical', 'empty_canonical',
  'orphan_page', 'thin_content',
  'missing_structured_data', 'json_ld_invalid_json', 'microdata_unknown_type', 'rdfa_unknown_type',
]

function backendIssueTypes(): string[] {
  const modules = join(__dirname, '..', '..', 'backend', 'modules')
  if (!existsSync(modules)) return []
  const found = new Set<string>()
  for (const file of readdirSync(modules)) {
    if (!file.endsWith('.py') || /translations|report_generator/.test(file)) continue
    const source = readFileSync(join(modules, file), 'utf8')
    for (const m of source.matchAll(/'issue_type':\s*'([a-z0-9_]+)'/g)) found.add(m[1])
    for (const m of source.matchAll(/issue_type='([a-z0-9_]+)'/g)) found.add(m[1])
    for (const m of source.matchAll(/'(broken_[a-z]+)'/g)) found.add(m[1])
  }
  return [...found]
}

describe('every backend issue type has a place in the report', () => {
  const types = [...new Set([...STATIC_BACKEND_TYPES, ...backendIssueTypes()])].sort()

  it.each(types)('%s is shown in exactly one section', (type) => {
    const results = scanResults([issue(type, 'medium')])
    const owners = SECTIONS.filter((section) => section.issues(results).length > 0).map((s) => s.id)
    expect(owners, `${type} -> [${owners.join(', ')}]`).toHaveLength(1)
  })
})

describe('regressions: types the backend emits that no section used to show', () => {
  it('shows missing_structured_data in Structured Data', () => {
    const issues = [issue('missing_structured_data', 'medium'), issue('thin_content', 'high')]
    expect(getStructuredDataIssues(issues).map((i) => i.issue_type)).toEqual(['missing_structured_data'])
  })

  it('shows empty_canonical under Canonical, in the Missing tab', () => {
    const issues = [issue('empty_canonical', 'medium'), issue('missing_canonical', 'low')]
    expect(getCanonicalIssues(issues)).toHaveLength(2)
    expect(getMissingCanonical(issues)).toHaveLength(2)
  })
})
