// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { useEffect, useState } from 'react'

function prefersReducedMotion(): boolean {
  return (
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  )
}

/**
 * Animates an integer from 0 to `target` (ease-out). Jumps straight to the
 * target when the user prefers reduced motion or rAF is unavailable.
 */
export function useCountUp(target: number, duration = 1100): number {
  const instant = prefersReducedMotion() || typeof requestAnimationFrame !== 'function'
  const [value, setValue] = useState(instant ? target : 0)

  useEffect(() => {
    if (prefersReducedMotion() || typeof requestAnimationFrame !== 'function') {
      setValue(target)
      return
    }
    let frame = 0
    let startedAt: number | null = null
    const tick = (now: number) => {
      // Anchor to the first frame's timestamp: in jsdom the callback can fire
      // with a clock earlier than the render, which would make progress negative.
      if (startedAt === null) startedAt = now
      const progress = Math.min(1, Math.max(0, (now - startedAt) / duration))
      const eased = 1 - Math.pow(1 - progress, 3)
      setValue(Math.round(target * eased))
      if (progress < 1) frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [target, duration])

  return value
}
