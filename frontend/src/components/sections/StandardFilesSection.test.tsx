// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { StandardFilesSection } from './StandardFilesSection'
import { issue } from '../../test/fixtures'

describe('StandardFilesSection', () => {
  const issues = [
    issue('robots_txt_found', 'info', 'https://example.com/robots.txt'),
    issue('sitemap_found', 'info', 'https://example.com/sitemap.xml'),
    issue('missing_llms_txt', 'info', 'https://example.com'),
    issue('missing_security_txt', 'info', 'https://example.com'),
  ]

  it('counts only the files that were found', () => {
    render(<StandardFilesSection issues={issues} />)
    expect(screen.getByText('2 standard files found')).toBeInTheDocument()
  })

  it('draws found files as success and missing ones as plain issues', () => {
    const { container } = render(<StandardFilesSection issues={issues} />)
    const cards = [...container.querySelectorAll('div.relative.overflow-hidden')]
    const toneOf = (label: string) =>
      cards.find((card) => card.textContent?.includes(label))?.className ?? ''

    expect(toneOf('robots.txt')).toContain('success')
    expect(toneOf('Missing llms.txt')).not.toContain('success')
    expect(toneOf('Missing security.txt')).not.toContain('success')
  })
})
