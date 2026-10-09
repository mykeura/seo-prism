// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { IssueCard } from './IssueCard'
import { issue } from '../test/fixtures'

describe('IssueCard', () => {
  it('shows the readable type, severity, url and description', () => {
    render(<IssueCard issue={issue('broken_link', 'high', 'https://example.com/gone')} />)

    expect(screen.getByText('Broken Link')).toBeInTheDocument()
    expect(screen.getByText('High')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'https://example.com/gone' })).toHaveAttribute(
      'href',
      'https://example.com/gone',
    )
    expect(screen.getByText('broken_link on https://example.com/gone')).toBeInTheDocument()
  })

  it('opens links safely in a new tab', () => {
    render(<IssueCard issue={issue('broken_link', 'low')} />)
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', expect.stringContaining('noopener'))
  })

  it('shows the source page only when asked to, and only when it differs in text-if-different mode', () => {
    const page = issue('missing_h1', 'high', 'https://example.com/a', { source_page: 'https://example.com/a' })
    const other = issue('broken_link', 'medium', 'https://example.com/x', { source_page: 'https://example.com/from' })

    const { rerender } = render(<IssueCard issue={other} />)
    expect(screen.queryByText('Source:')).toBeNull()

    rerender(<IssueCard issue={other} sourceMode="link" />)
    expect(screen.getByRole('link', { name: 'https://example.com/from' })).toBeInTheDocument()

    rerender(<IssueCard issue={page} sourceMode="text-if-different" />)
    expect(screen.queryByText('Source:')).toBeNull()

    rerender(<IssueCard issue={other} sourceMode="text-if-different" />)
    expect(screen.getByText('https://example.com/from')).toBeInTheDocument()
  })

  it('falls back to the raw type for unknown issue types', () => {
    render(<IssueCard issue={issue('brand_new_type', 'low', 'https://example.com/z', { description: undefined })} />)
    expect(screen.getByText('brand_new_type')).toBeInTheDocument()
  })
})
