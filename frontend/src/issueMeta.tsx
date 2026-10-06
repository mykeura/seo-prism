// SPDX-License-Identifier: AGPL-3.0-only
// SPDX-FileCopyrightText: 2026 mykeura <mykeura@hotmail.com>

import type { ReactNode } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faLink,
  faFileAlt,
  faFileImage,
  faTag,
  faRobot,
  faShieldAlt,
  faMap,
  faFolder,
  faExclamationTriangle,
  faGlobe,
  faDatabase,
  faBrain
} from '@fortawesome/free-solid-svg-icons'
import type { IconDefinition } from '@fortawesome/fontawesome-svg-core'
import type { SeverityVariant } from './types'

const severityVariants: Record<string, SeverityVariant> = {
  high: 'destructive',
  medium: 'warning',
  low: 'secondary',
  info: 'default',
}

export function getSeverityColor(severity: string): SeverityVariant {
  return severityVariants[severity] ?? 'outline'
}

const gradeColors: Record<string, string> = {
  A: 'text-success-300 border-success-400/25 bg-success-500/10',
  B: 'text-primary-300 border-primary-400/25 bg-primary-500/10',
  C: 'text-warning-300 border-warning-400/25 bg-warning-500/10',
  D: 'text-warning-500 border-warning-500/25 bg-warning-500/10',
  F: 'text-danger-300 border-danger-400/25 bg-danger-500/10',
}

export function getGradeColor(grade: string): string {
  return gradeColors[grade] ?? 'text-muted-foreground border-border bg-muted/30'
}

export function getIssueTypeLabel(type: string, labels: Record<string, string>): string {
  return labels[type] ?? type
}

interface IssueIconMeta {
  icon: IconDefinition
  className: string
}

const issueIcons: Record<string, IssueIconMeta> = {
  broken_link: { icon: faLink, className: 'text-destructive' },
  broken_image: { icon: faLink, className: 'text-destructive' },
  broken_script: { icon: faLink, className: 'text-destructive' },
  broken_stylesheet: { icon: faLink, className: 'text-destructive' },
  broken_resource: { icon: faLink, className: 'text-destructive' },
  missing_title: { icon: faFileAlt, className: 'text-primary-400' },
  missing_description: { icon: faFileAlt, className: 'text-primary-400' },
  title_too_short: { icon: faFileAlt, className: 'text-warning' },
  title_too_long: { icon: faFileAlt, className: 'text-warning' },
  meta_description_too_short: { icon: faFileAlt, className: 'text-warning' },
  meta_description_too_long: { icon: faFileAlt, className: 'text-warning' },
  duplicate_title: { icon: faFileAlt, className: 'text-warning' },
  duplicate_description: { icon: faFileAlt, className: 'text-warning' },
  missing_alt_tag: { icon: faFileImage, className: 'text-secondary' },
  missing_alt_text: { icon: faFileImage, className: 'text-secondary' },
  short_alt_text: { icon: faFileImage, className: 'text-secondary' },
  robots_txt_found: { icon: faRobot, className: 'text-success' },
  security_txt_found: { icon: faShieldAlt, className: 'text-success' },
  sitemap_found: { icon: faMap, className: 'text-success' },
  llms_txt_found: { icon: faBrain, className: 'text-success' },
  missing_robots_txt: { icon: faRobot, className: 'text-destructive' },
  missing_security_txt: { icon: faShieldAlt, className: 'text-destructive' },
  missing_sitemap: { icon: faMap, className: 'text-destructive' },
  missing_llms_txt: { icon: faBrain, className: 'text-secondary' },
  meta_robots_noindex: { icon: faRobot, className: 'text-destructive' },
  meta_robots_nofollow: { icon: faRobot, className: 'text-warning' },
  meta_robots_nosnippet: { icon: faRobot, className: 'text-warning' },
  meta_robots_noarchive: { icon: faRobot, className: 'text-secondary' },
  meta_robots_notranslate: { icon: faRobot, className: 'text-secondary' },
  meta_robots_noimageindex: { icon: faRobot, className: 'text-warning' },
  meta_robots_unavailable_after: { icon: faRobot, className: 'text-secondary' },
  missing_h1: { icon: faTag, className: 'text-destructive' },
  multiple_h1_same_page: { icon: faTag, className: 'text-destructive' },
  duplicate_h1: { icon: faTag, className: 'text-warning' },
  invalid_header_hierarchy: { icon: faTag, className: 'text-warning' },
  hreflang_missing_self_reference: { icon: faGlobe, className: 'text-destructive' },
  hreflang_missing_x_default: { icon: faGlobe, className: 'text-warning' },
  hreflang_duplicate_code: { icon: faGlobe, className: 'text-destructive' },
  hreflang_invalid_code: { icon: faGlobe, className: 'text-destructive' },
  hreflang_missing_return_link: { icon: faGlobe, className: 'text-destructive' },
  hreflang_missing_canonical: { icon: faGlobe, className: 'text-destructive' },
  canonical_chain: { icon: faLink, className: 'text-destructive' },
  canonical_to_404: { icon: faLink, className: 'text-destructive' },
  canonical_to_redirect: { icon: faLink, className: 'text-warning' },
  canonical_url_variation: { icon: faLink, className: 'text-secondary' },
  missing_canonical: { icon: faLink, className: 'text-secondary' },
  orphan_page: { icon: faFolder, className: 'text-warning' },
  missing_json_ld: { icon: faDatabase, className: 'text-secondary' },
  json_ld_missing_type: { icon: faDatabase, className: 'text-destructive' },
  json_ld_unknown_type: { icon: faDatabase, className: 'text-warning' },
  json_ld_missing_properties: { icon: faDatabase, className: 'text-destructive' },
  json_ld_short_headline: { icon: faDatabase, className: 'text-warning' },
  json_ld_invalid_json: { icon: faDatabase, className: 'text-destructive' },
  missing_microdata: { icon: faDatabase, className: 'text-secondary' },
  microdata_missing_type: { icon: faDatabase, className: 'text-destructive' },
  microdata_unknown_type: { icon: faDatabase, className: 'text-warning' },
  missing_rdfa: { icon: faDatabase, className: 'text-secondary' },
  rdfa_unknown_type: { icon: faDatabase, className: 'text-warning' },
  thin_content: { icon: faFileAlt, className: 'text-warning' },
}

export function getIssueIcon(type: string): ReactNode {
  const meta = issueIcons[type]
  if (!meta) {
    return <FontAwesomeIcon icon={faExclamationTriangle} className="text-outline" />
  }
  return <FontAwesomeIcon icon={meta.icon} className={meta.className} />
}

