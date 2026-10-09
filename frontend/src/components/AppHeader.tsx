// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { APP_VERSION } from '../version'

export function AppHeader() {
  return (
    <header className="flex items-center justify-between py-5">
      <div className="flex items-center gap-2.5">
        <img src="/logo.png" alt="" width={28} height={28} className="h-7 w-7" />
        <span className="font-display text-base font-semibold tracking-tight">SEO Prism</span>
      </div>
      <span className="font-mono text-xs text-muted-foreground">v{APP_VERSION}</span>
    </header>
  )
}
