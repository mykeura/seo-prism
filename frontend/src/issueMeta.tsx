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

const issueTypeLabels: Record<string, string> = {
  broken_link: 'Broken Link',
  broken_image: 'Broken Image',
  broken_script: 'Broken Script',
  broken_stylesheet: 'Broken Stylesheet',
  broken_resource: 'Broken Resource',
  missing_title: 'Missing Title',
  missing_description: 'Missing Description',
  title_too_short: 'Title Too Short',
  title_too_long: 'Title Too Long',
  meta_description_too_short: 'Meta Description Too Short',
  meta_description_too_long: 'Meta Description Too Long',
  duplicate_title: 'Duplicate Title',
  duplicate_description: 'Duplicate Description',
  missing_alt_tag: 'Missing Alt Tag',
  missing_alt_text: 'Missing Alt Text',
  short_alt_text: 'Short Alt Text',
  missing_robots_txt: 'Missing robots.txt',
  missing_security_txt: 'Missing security.txt',
  missing_sitemap: 'Missing Sitemap',
  missing_llms_txt: 'Missing llms.txt',
  robots_txt_found: 'robots.txt',
  security_txt_found: 'security.txt',
  sitemap_found: 'Sitemap',
  llms_txt_found: 'llms.txt',
  meta_robots_noindex: 'Noindex Directive',
  meta_robots_nofollow: 'Nofollow Directive',
  meta_robots_nosnippet: 'Nosnippet Directive',
  meta_robots_noarchive: 'Noarchive Directive',
  meta_robots_notranslate: 'Notranslate Directive',
  meta_robots_noimageindex: 'Noimageindex Directive',
  meta_robots_unavailable_after: 'Unavailable After Directive',
  missing_h1: 'Missing H1 Header',
  multiple_h1_same_page: 'Multiple H1 Headers on Same Page',
  duplicate_h1: 'Duplicate H1 Header',
  invalid_header_hierarchy: 'Invalid Header Hierarchy',
  hreflang_missing_self_reference: 'Hreflang Missing Self Reference',
  hreflang_missing_x_default: 'Hreflang Missing x-default',
  hreflang_duplicate_code: 'Hreflang Duplicate Code',
  hreflang_invalid_code: 'Hreflang Invalid Code',
  hreflang_missing_return_link: 'Hreflang Missing Return Link',
  hreflang_missing_canonical: 'Hreflang Missing Canonical',
  canonical_chain: 'Canonical Chain',
  canonical_to_404: 'Canonical to 404',
  canonical_to_redirect: 'Canonical to Redirect',
  canonical_url_variation: 'Canonical URL Variation',
  missing_canonical: 'Missing Canonical',
  orphan_page: 'Orphan Page',
  missing_json_ld: 'Missing JSON-LD',
  json_ld_missing_type: 'JSON-LD Missing Type',
  json_ld_unknown_type: 'JSON-LD Unknown Type',
  json_ld_missing_properties: 'JSON-LD Missing Properties',
  json_ld_short_headline: 'JSON-LD Short Headline',
  json_ld_invalid_json: 'JSON-LD Invalid JSON',
  missing_microdata: 'Missing Microdata',
  microdata_missing_type: 'Microdata Missing Type',
  microdata_unknown_type: 'Microdata Unknown Type',
  missing_rdfa: 'Missing RDFa',
  rdfa_unknown_type: 'RDFa Unknown Type',
  thin_content: 'Thin Content',
}

export function getIssueTypeLabel(type: string): string {
  return issueTypeLabels[type] ?? type
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

