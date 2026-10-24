// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faClockRotateLeft } from '@fortawesome/free-solid-svg-icons'
import { Button } from './ui/button'
import { APP_VERSION } from '../version'
import { useT } from '../i18n'

interface AppHeaderProps {
  historyOpen: boolean
  onToggleHistory: () => void
}

export function AppHeader({ historyOpen, onToggleHistory }: AppHeaderProps) {
  const t = useT()

  return (
    <header className="flex items-center justify-between py-5">
      <div className="flex items-center gap-2.5">
        <img src="/logo.png" alt="" width={28} height={28} className="h-7 w-7" />
        <span className="font-display text-base font-semibold tracking-tight">SEO Prism</span>
      </div>
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggleHistory}
          aria-expanded={historyOpen}
          aria-controls="scan-history"
        >
          <FontAwesomeIcon icon={faClockRotateLeft} aria-hidden="true" />
          {t.history.title}
        </Button>
        <span className="font-mono text-xs text-muted-foreground">v{APP_VERSION}</span>
      </div>
    </header>
  )
}
