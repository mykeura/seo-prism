// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { useId } from 'react'
import { useCountUp } from '../hooks/useCountUp'
import { useT } from '../i18n'

interface GradeGaugeProps {
  score: number
  grade: string
}

// Colour tokens per grade (all exist in the theme palette).
const gradeTone: Record<string, { from: string; to: string }> = {
  A: { from: 'var(--color-success-300)', to: 'var(--color-success-500)' },
  B: { from: 'var(--color-primary-300)', to: 'var(--color-primary-500)' },
  C: { from: 'var(--color-warning-300)', to: 'var(--color-warning-500)' },
  D: { from: 'var(--color-warning-400)', to: 'var(--color-warning-600)' },
  F: { from: 'var(--color-danger-300)', to: 'var(--color-danger-500)' },
}
const fallbackTone = { from: 'var(--color-outline)', to: 'var(--color-muted-foreground)' }

const RADIUS = 84
const CIRCUMFERENCE = 2 * Math.PI * RADIUS
const ARC = CIRCUMFERENCE * 0.75 // 270 degrees, open at the bottom

export function clampScore(score: number): number {
  if (!Number.isFinite(score)) return 0
  return Math.max(0, Math.min(100, Math.round(score)))
}

/**
 * The SEO grade as an instrument dial: a 270 degree arc that fills to the
 * score while the number counts up. The letter is the headline.
 */
export function GradeGauge({ score, grade }: GradeGaugeProps) {
  const t = useT()
  const gradientId = `gauge-${useId().replace(/:/g, '')}`
  const finalScore = clampScore(score)
  const shown = useCountUp(finalScore)
  const tone = gradeTone[grade] ?? fallbackTone
  const filled = (ARC * shown) / 100

  return (
    <div
      role="img"
      aria-label={t.overview.gradeLabel(grade, finalScore)}
      className="relative mx-auto h-[210px] w-[210px] shrink-0"
    >
      <svg viewBox="0 0 200 200" className="h-full w-full" aria-hidden="true">
        <defs>
          <linearGradient id={gradientId} x1="0" y1="1" x2="1" y2="0">
            <stop offset="0%" style={{ stopColor: tone.to }} />
            <stop offset="100%" style={{ stopColor: tone.from }} />
          </linearGradient>
        </defs>
        <g transform="rotate(135 100 100)" fill="none" strokeLinecap="round">
          <circle
            cx="100"
            cy="100"
            r={RADIUS}
            strokeWidth="12"
            stroke="rgba(255,255,255,0.07)"
            strokeDasharray={`${ARC} ${CIRCUMFERENCE}`}
          />
          {shown > 0 && (
            <circle
              cx="100"
              cy="100"
              r={RADIUS}
              strokeWidth="12"
              stroke={`url(#${gradientId})`}
              strokeDasharray={`${filled} ${CIRCUMFERENCE}`}
              style={{ filter: `drop-shadow(0 0 10px color-mix(in oklab, ${tone.from} 45%, transparent))` }}
            />
          )}
        </g>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center pb-3">
        <span
          className="font-display text-7xl font-extrabold leading-none tracking-tight"
          style={{ color: tone.from }}
        >
          {grade}
        </span>
        <span className="mt-2 text-sm tabular-nums text-muted-foreground">
          {t.overview.scoreOutOf(shown)}
        </span>
      </div>
    </div>
  )
}
