// SPDX-License-Identifier: AGPL-3.0-only
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import type { Issue } from './types'

export function isInternalUrl(url: string, baseUrl: string): boolean {
  try {
    const urlObj = new URL(url)
    const baseUrlObj = new URL(baseUrl)
    return urlObj.hostname === baseUrlObj.hostname
  } catch {
    return false
  }
}

export function getBrokenLinkIssues(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'broken_link' ||
    issue.issue_type === 'broken_image' ||
    issue.issue_type === 'broken_script' ||
    issue.issue_type === 'broken_stylesheet' ||
    issue.issue_type === 'broken_resource'
  )
}

export function getInternalLinks(issues: Issue[], baseUrl: string): Issue[] {
  return issues.filter(issue =>
    isInternalUrl(issue.url, baseUrl)
  )
}

export function getExternalLinks(issues: Issue[], baseUrl: string): Issue[] {
  return issues.filter(issue =>
    !isInternalUrl(issue.url, baseUrl)
  )
}

export function getMetaTagsIssues(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'missing_title' ||
    issue.issue_type === 'missing_description' ||
    issue.issue_type === 'duplicate_title' ||
    issue.issue_type === 'duplicate_description'
  )
}

export function getMissingTitles(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'missing_title' ||
    issue.issue_type === 'duplicate_title'
  )
}

export function getMissingDescriptions(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'missing_description' ||
    issue.issue_type === 'duplicate_description'
  )
}

export function getMetaLengthIssues(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'title_too_short' ||
    issue.issue_type === 'title_too_long' ||
    issue.issue_type === 'meta_description_too_short' ||
    issue.issue_type === 'meta_description_too_long'
  )
}

export function getTitleLengthIssues(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'title_too_short' ||
    issue.issue_type === 'title_too_long'
  )
}

export function getMetaDescLengthIssues(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'meta_description_too_short' ||
    issue.issue_type === 'meta_description_too_long'
  )
}

export function getStandardFilesIssues(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'robots_txt_found' ||
    issue.issue_type === 'security_txt_found' ||
    issue.issue_type === 'sitemap_found' ||
    issue.issue_type === 'llms_txt_found' ||
    issue.issue_type === 'missing_robots_txt' ||
    issue.issue_type === 'missing_security_txt' ||
    issue.issue_type === 'missing_sitemap' ||
    issue.issue_type === 'missing_llms_txt'
  )
}

export function getMetaRobotsIssues(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type.startsWith('meta_robots_')
  )
}

export function getHreflangIssues(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'hreflang_missing_self_reference' ||
    issue.issue_type === 'hreflang_missing_x_default' ||
    issue.issue_type === 'hreflang_duplicate_code' ||
    issue.issue_type === 'hreflang_invalid_code' ||
    issue.issue_type === 'hreflang_missing_return_link' ||
    issue.issue_type === 'hreflang_missing_canonical'
  )
}

export function getCanonicalIssues(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'canonical_chain' ||
    issue.issue_type === 'canonical_to_404' ||
    issue.issue_type === 'canonical_to_redirect' ||
    issue.issue_type === 'canonical_url_variation' ||
    issue.issue_type === 'missing_canonical'
  )
}

export function getCanonicalChains(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'canonical_chain'
  )
}

export function getCanonical404(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'canonical_to_404'
  )
}

export function getCanonicalRedirect(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'canonical_to_redirect'
  )
}

export function getCanonicalVariations(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'canonical_url_variation'
  )
}

export function getMissingCanonical(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'missing_canonical'
  )
}

export function getOrphanPagesIssues(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'orphan_page'
  )
}

export function getStructuredDataIssues(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type.startsWith('json_ld') ||
    issue.issue_type.startsWith('microdata') ||
    issue.issue_type.startsWith('rdfa')
  )
}

export function getMissingAltTagIssues(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'missing_alt_tag' ||
    issue.issue_type === 'missing_alt_text' ||
    issue.issue_type === 'short_alt_text'
  )
}

export function getH1Issues(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'missing_h1' ||
    issue.issue_type === 'multiple_h1_same_page' ||
    issue.issue_type === 'duplicate_h1'
  )
}

export function getHeaderHierarchyIssues(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'invalid_header_hierarchy'
  )
}

export function getHeaderIssues(issues: Issue[]): Issue[] {
  return issues.filter(issue =>
    issue.issue_type === 'missing_h1' ||
    issue.issue_type === 'multiple_h1_same_page' ||
    issue.issue_type === 'duplicate_h1' ||
    issue.issue_type === 'invalid_header_hierarchy'
  )
}

export function getThinContentIssues(issues: Issue[]): Issue[] {
  return issues.filter(i => i.issue_type === 'thin_content')
}
