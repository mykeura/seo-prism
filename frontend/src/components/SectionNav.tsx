// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCheck } from '@fortawesome/free-solid-svg-icons'
import { cn } from '../lib/utils'
import { severityText } from '../issueMeta'
import { SECTIONS, type SectionSummary } from '../sections'
import { useT } from '../i18n'

interface SectionNavProps {
  summaries: SectionSummary[]
  activeId: string
  onSelect: (id: string) => void
}

/**
 * Report navigation: a sticky list on large screens, a scrollable strip on
 * small ones. Each entry carries its issue count and the colour of its most
 * serious severity.
 */
export function SectionNav({ summaries, activeId, onSelect }: SectionNavProps) {
  const t = useT()

  return (
    <nav
      aria-label={t.nav.label}
      className="-mx-4 flex gap-2 overflow-x-auto px-4 pb-1 [scrollbar-width:none] lg:sticky lg:top-6 lg:mx-0 lg:flex-col lg:gap-0.5 lg:overflow-visible lg:px-0 lg:pb-0"
    >
      {SECTIONS.map((section) => {
        const summary = summaries.find((item) => item.id === section.id)
        const count = summary?.count ?? 0
        const active = section.id === activeId
        const title = section.title(t)

        return (
          <button
            key={section.id}
            type="button"
            aria-current={active ? 'true' : undefined}
            onClick={() => onSelect(section.id)}
            className={cn(
              'nav-marker flex shrink-0 items-center gap-3 rounded-full border px-3.5 py-2 text-left text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 lg:rounded-lg lg:border-transparent lg:px-3 lg:py-2.5',
              active
                ? 'border-white/15 bg-white/[0.07] text-foreground'
                : 'border-white/10 text-muted-foreground hover:bg-white/[0.04] hover:text-foreground',
            )}
          >
            <FontAwesomeIcon
              icon={section.icon}
              className={cn('w-4 shrink-0 text-xs', summary?.worst ? severityText[summary.worst] : 'text-muted-foreground/60')}
            />
            <span className="whitespace-nowrap font-medium lg:flex-1">{title}</span>
            {count > 0 ? (
              <span className="rounded-full bg-white/10 px-2 py-0.5 text-xs font-medium tabular-nums text-foreground">
                {count}
              </span>
            ) : (
              <>
                <FontAwesomeIcon icon={faCheck} className="hidden text-xs text-success-400 lg:inline" aria-hidden="true" />
                <span className="sr-only">{t.nav.clean}</span>
              </>
            )}
          </button>
        )
      })}
    </nav>
  )
}
