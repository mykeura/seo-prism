// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { SeverityBar, countBySeverity } from './SeverityBar'
import { issue } from '../test/fixtures'

describe('countBySeverity', () => {
  it('counts each severity and ignores unknown ones', () => {
    const counts = countBySeverity([
      issue('a', 'high'), issue('b', 'high'), issue('c', 'low'), issue('d', 'info'), issue('e', 'weird'),
    ])
    expect(counts).toEqual({ high: 2, medium: 0, low: 1, info: 1 })
  })
})

describe('SeverityBar', () => {
  it('sizes slices in proportion and describes them for screen readers', () => {
    const { container } = render(<SeverityBar counts={{ high: 6, medium: 3, low: 1, info: 0 }} />)

    const bar = screen.getByRole('img', { name: /Issues by severity.*High: 6.*Medium: 3.*Low: 1/ })
    expect(bar).toBeInTheDocument()
    expect(container.querySelector('[data-severity="high"]')).toHaveStyle({ flexGrow: '6' })
    expect(container.querySelector('[data-severity="medium"]')).toHaveStyle({ flexGrow: '3' })
    expect(container.querySelector('[data-severity="info"]')).toBeNull()
  })

  it('lists every severity in the legend, zeros included', () => {
    render(<SeverityBar counts={{ high: 0, medium: 2, low: 0, info: 0 }} />)
    const legend = screen.getAllByRole('listitem')
    expect(legend).toHaveLength(4)
    expect(legend[0]).toHaveTextContent('High0')
    expect(legend[1]).toHaveTextContent('Medium2')
  })

  it('renders an empty track when there are no issues', () => {
    const { container } = render(<SeverityBar counts={{ high: 0, medium: 0, low: 0, info: 0 }} />)
    expect(container.querySelectorAll('[data-severity]')).toHaveLength(0)
  })
})
