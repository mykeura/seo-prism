// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { GradeGauge, clampScore } from './GradeGauge'

describe('clampScore', () => {
  it('rounds and clamps to 0-100', () => {
    expect(clampScore(84.4)).toBe(84)
    expect(clampScore(-5)).toBe(0)
    expect(clampScore(250)).toBe(100)
    expect(clampScore(Number.NaN)).toBe(0)
  })
})

describe('GradeGauge', () => {
  it('announces the grade and the final score straight away', () => {
    render(<GradeGauge score={84} grade="B" />)
    expect(screen.getByRole('img', { name: 'SEO grade B, 84 out of 100' })).toBeInTheDocument()
    expect(screen.getByText('B')).toBeInTheDocument()
  })

  it('never announces an out-of-range score', () => {
    render(<GradeGauge score={140} grade="A" />)
    expect(screen.getByRole('img', { name: 'SEO grade A, 100 out of 100' })).toBeInTheDocument()
  })

  it('counts up to the score', async () => {
    render(<GradeGauge score={71} grade="C" />)
    expect(await screen.findByText('71 / 100', undefined, { timeout: 3000 })).toBeInTheDocument()
  })

  it('shows the final value at once when the user prefers reduced motion', () => {
    vi.stubGlobal('matchMedia', (query: string) => ({
      matches: true,
      media: query,
      addEventListener() {},
      removeEventListener() {},
    }))
    try {
      render(<GradeGauge score={92} grade="A" />)
      expect(screen.getByText('92 / 100')).toBeInTheDocument()
    } finally {
      vi.unstubAllGlobals()
    }
  })
})
