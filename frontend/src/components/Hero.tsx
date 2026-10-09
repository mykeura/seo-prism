// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { RefractionBeam } from './RefractionBeam'
import { useT } from '../i18n'

/**
 * Landing view: the prism splitting a ray into the palette, then the one
 * sentence that says what the tool does.
 */
export function Hero({ scanning }: { scanning: boolean }) {
  const t = useT()

  return (
    <section className="text-center">
      <div className="relative mx-auto h-48 w-full max-w-5xl overflow-hidden sm:h-60">
        <RefractionBeam active={scanning} />
        <div
          aria-hidden="true"
          className="absolute left-1/2 top-1/2 h-44 w-44 -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(circle,hsl(262_70%_60%/0.34),hsl(220_75%_58%/0.12)_45%,transparent_70%)] blur-xl"
        />
        <img
          src="/logo.png"
          alt=""
          width={120}
          height={120}
          className="absolute left-1/2 top-1/2 h-[112px] w-[112px] -translate-x-1/2 -translate-y-1/2"
        />
      </div>

      <h1 className="mx-auto mt-2 max-w-3xl text-balance font-display text-4xl font-bold leading-[1.08] tracking-[-0.03em] sm:text-5xl lg:text-[3.5rem]">
        {t.hero.title}
      </h1>
      <p className="mx-auto mt-5 max-w-2xl text-balance text-base leading-relaxed text-muted-foreground sm:text-lg">
        {t.app.subtitle}
      </p>
    </section>
  )
}
