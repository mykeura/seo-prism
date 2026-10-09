// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import type { ReactNode } from 'react'
import {
  faDatabase,
  faFileAlt,
  faFileImage,
  faFolder,
  faGlobe,
  faLink,
  faRobot,
  faTag,
} from '@fortawesome/free-solid-svg-icons'
import type { IconDefinition } from '@fortawesome/fontawesome-svg-core'
import { BrokenLinksSection } from './components/sections/BrokenLinksSection'
import { MetaTagsSection } from './components/sections/MetaTagsSection'
import { MetaLengthSection } from './components/sections/MetaLengthSection'
import { ImagesAltSection } from './components/sections/ImagesAltSection'
import { HeaderAnalysisSection } from './components/sections/HeaderAnalysisSection'
import { StandardFilesSection } from './components/sections/StandardFilesSection'
import { MetaRobotsSection } from './components/sections/MetaRobotsSection'
import { HreflangSection } from './components/sections/HreflangSection'
import { CanonicalSection } from './components/sections/CanonicalSection'
import { OrphanPagesSection } from './components/sections/OrphanPagesSection'
import { StructuredDataSection } from './components/sections/StructuredDataSection'
import { ThinContentSection } from './components/sections/ThinContentSection'
import {
  getBrokenLinkIssues,
  getCanonicalIssues,
  getHeaderIssues,
  getHreflangIssues,
  getMetaLengthIssues,
  getMetaRobotsIssues,
  getMetaTagsIssues,
  getMissingAltTagIssues,
  getOrphanPagesIssues,
  getStandardFilesIssues,
  getStructuredDataIssues,
  getThinContentIssues,
} from './filters'
import { SEVERITY_ORDER, isSeverity, type Severity } from './issueMeta'
import type { Translations } from './i18n/en'
import type { Issue, ScanResults } from './types'

export interface SectionDef {
  id: string
  title: (t: Translations) => string
  icon: IconDefinition
  issues: (results: ScanResults) => Issue[]
  render: (results: ScanResults) => ReactNode
}

/** Report sections, in display order. */
export const SECTIONS: SectionDef[] = [
  {
    id: 'brokenLinks',
    title: (t) => t.sections.brokenLinks.title,
    icon: faLink,
    issues: (r) => getBrokenLinkIssues(r.issues),
    render: (r) => <BrokenLinksSection results={r} />,
  },
  {
    id: 'metaTags',
    title: (t) => t.sections.metaTags.title,
    icon: faFileAlt,
    issues: (r) => getMetaTagsIssues(r.issues),
    render: (r) => <MetaTagsSection issues={r.issues} />,
  },
  {
    id: 'metaLength',
    title: (t) => t.sections.metaLength.title,
    icon: faFileAlt,
    issues: (r) => getMetaLengthIssues(r.issues),
    render: (r) => <MetaLengthSection issues={r.issues} />,
  },
  {
    id: 'imagesAlt',
    title: (t) => t.sections.imagesAlt.title,
    icon: faFileImage,
    issues: (r) => getMissingAltTagIssues(r.issues),
    render: (r) => <ImagesAltSection issues={r.issues} />,
  },
  {
    id: 'headerAnalysis',
    title: (t) => t.sections.headerAnalysis.title,
    icon: faTag,
    issues: (r) => getHeaderIssues(r.issues),
    render: (r) => <HeaderAnalysisSection issues={r.issues} />,
  },
  {
    id: 'standardFiles',
    title: (t) => t.sections.standardFiles.title,
    icon: faFolder,
    issues: (r) => getStandardFilesIssues(r.issues),
    render: (r) => <StandardFilesSection issues={r.issues} />,
  },
  {
    id: 'metaRobots',
    title: (t) => t.sections.metaRobots.title,
    icon: faRobot,
    issues: (r) => getMetaRobotsIssues(r.issues),
    render: (r) => <MetaRobotsSection issues={r.issues} />,
  },
  {
    id: 'hreflang',
    title: (t) => t.sections.hreflang.title,
    icon: faGlobe,
    issues: (r) => getHreflangIssues(r.issues),
    render: (r) => <HreflangSection issues={r.issues} />,
  },
  {
    id: 'canonical',
    title: (t) => t.sections.canonical.title,
    icon: faLink,
    issues: (r) => getCanonicalIssues(r.issues),
    render: (r) => <CanonicalSection issues={r.issues} />,
  },
  {
    id: 'orphanPages',
    title: (t) => t.sections.orphanPages.title,
    icon: faFolder,
    issues: (r) => getOrphanPagesIssues(r.issues),
    render: (r) => <OrphanPagesSection issues={r.issues} />,
  },
  {
    id: 'structuredData',
    title: (t) => t.sections.structuredData.title,
    icon: faDatabase,
    issues: (r) => getStructuredDataIssues(r.issues),
    render: (r) => <StructuredDataSection issues={r.issues} />,
  },
  {
    id: 'thinContent',
    title: (t) => t.sections.thinContent.title,
    icon: faFileAlt,
    issues: (r) => getThinContentIssues(r.issues),
    render: (r) => <ThinContentSection issues={r.issues} />,
  },
]

export interface SectionSummary {
  id: string
  /** Issues that need attention (everything except info-level notices). */
  count: number
  /** Most serious severity present in the section, or null when it is empty. */
  worst: Severity | null
}

export function worstSeverity(issues: Issue[]): Severity | null {
  for (const severity of SEVERITY_ORDER) {
    if (issues.some((issue) => issue.severity === severity)) return severity
  }
  return null
}

export function summarizeSections(results: ScanResults): SectionSummary[] {
  return SECTIONS.map((section) => {
    const issues = section.issues(results)
    return {
      id: section.id,
      count: issues.filter((issue) => issue.severity !== 'info' && isSeverity(issue.severity)).length,
      worst: worstSeverity(issues),
    }
  })
}

/** The section worth opening first: the one holding the most serious issues. */
export function defaultSectionId(summaries: SectionSummary[]): string {
  for (const severity of SEVERITY_ORDER) {
    if (severity === 'info') break
    const hit = summaries.find((summary) => summary.worst === severity)
    if (hit) return hit.id
  }
  return summaries[0]?.id ?? SECTIONS[0].id
}
