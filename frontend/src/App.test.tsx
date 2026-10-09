// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import App from './App'
import { LanguageProvider } from './i18n'
import { grade, issue, scanResults } from './test/fixtures'
import type { ScanResults } from './types'

function mockApi(options: {
  results?: ScanResults
  scan?: unknown
  scanStatus?: number
  networkError?: boolean
}) {
  const results = options.results ?? scanResults([])
  const fetchMock = vi.fn(async (input: RequestInfo | URL, _init?: RequestInit) => {
    if (options.networkError) throw new TypeError('Failed to fetch')
    const url = String(input)
    const json = (body: unknown, status = 200) =>
      new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })

    if (url.endsWith('/scan')) {
      return json(
        options.scan ?? { scan_id: 7, message: 'Scan completed', seo_grade: grade('B', 84) },
        options.scanStatus ?? 200,
      )
    }
    if (/\/results(\/\d+)?$/.test(url)) return json(results)
    throw new Error(`unexpected request: ${url}`)
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

async function scan(target: string) {
  const user = userEvent.setup()
  await user.type(screen.getByLabelText('Website URL'), target)
  await user.click(screen.getByRole('button', { name: 'Scan site' }))
}

const mixedResults = () =>
  scanResults([
    issue('broken_link', 'medium', 'https://example.com/gone', { source_page: 'https://example.com/' }),
    issue('missing_h1', 'high', 'https://example.com/a'),
    issue('missing_canonical', 'low', 'https://example.com/b'),
    issue('missing_structured_data', 'medium', 'https://example.com/c'),
    issue('robots_txt_found', 'info', 'https://example.com/robots.txt'),
  ])

describe('landing view', () => {
  it('shows the headline, the URL field and what gets checked', () => {
    render(<App />)

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('See how search engines read your site')
    expect(screen.getByLabelText('Website URL')).toBeInTheDocument()
    const checks = within(screen.getByRole('list', { name: 'What gets checked' })).getAllByRole('listitem')
    expect(checks).toHaveLength(12)
  })

  it('disables the scan button until a URL is typed', async () => {
    render(<App />)
    const button = screen.getByRole('button', { name: 'Scan site' })
    expect(button).toBeDisabled()

    await userEvent.setup().type(screen.getByLabelText('Website URL'), 'example.com')
    expect(button).toBeEnabled()
  })

  it('speaks Spanish when the browser does', () => {
    vi.spyOn(navigator, 'language', 'get').mockReturnValue('es-ES')
    render(
      <LanguageProvider>
        <App />
      </LanguageProvider>,
    )

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Descubre cómo leen tu sitio los buscadores')
    expect(screen.getByRole('button', { name: 'Analizar sitio' })).toBeInTheDocument()
  })
})

describe('running a scan', () => {
  it('adds the scheme, asks for this scan by id and shows the report', async () => {
    const fetchMock = mockApi({ results: mixedResults() })
    render(<App />)

    await scan('example.com')

    expect(await screen.findByRole('img', { name: 'SEO grade B, 84 out of 100' })).toBeInTheDocument()

    const [scanCall, resultsCall] = fetchMock.mock.calls
    expect(String(scanCall[0])).toMatch(/\/scan$/)
    expect(JSON.parse((scanCall[1] as RequestInit).body as string)).toEqual({ url: 'https://example.com' })
    expect(String(resultsCall[0])).toMatch(/\/results\/7$/)
  })

  it('uses http for local addresses', async () => {
    const fetchMock = mockApi({ results: mixedResults() })
    render(<App />)

    await scan('localhost:3000')
    await screen.findByRole('img', { name: /SEO grade/ })

    expect(JSON.parse((fetchMock.mock.calls[0][1] as RequestInit).body as string)).toEqual({
      url: 'http://localhost:3000',
    })
  })

  it('summarises pages and issues, leaving info notices out of the issue count', async () => {
    mockApi({ results: mixedResults() })
    render(<App />)
    await scan('example.com')
    await screen.findByRole('img', { name: /SEO grade/ })

    // 5 items came back, one is the info-level "robots.txt found"
    expect(screen.getByText('Pages Analyzed').nextElementSibling).toHaveTextContent('12')
    expect(screen.getByText('Issues').nextElementSibling).toHaveTextContent('4')
    expect(screen.getByText('Good', { exact: false })).toBeInTheDocument()
  })

  it('opens the section with the most serious issues and lets you move between sections', async () => {
    mockApi({ results: mixedResults() })
    render(<App />)
    await scan('example.com')
    await screen.findByRole('img', { name: /SEO grade/ })

    const nav = screen.getByRole('navigation', { name: 'Report sections' })
    // the only high-severity issue is a missing H1 -> Header Analysis opens first
    expect(within(nav).getByRole('button', { name: /Header Analysis/ })).toHaveAttribute('aria-current', 'true')
    expect(screen.getByText('Missing H1 Header')).toBeInTheDocument()

    await userEvent.setup().click(within(nav).getByRole('button', { name: /Structured Data/ }))

    expect(within(nav).getByRole('button', { name: /Structured Data/ })).toHaveAttribute('aria-current', 'true')
    // regression: this type used to be counted in the grade but never displayed
    expect(screen.getByText('Missing Structured Data')).toBeInTheDocument()
    expect(screen.queryByText('Missing H1 Header')).toBeNull()
  })

  it('shows the counts of each section in the navigation', async () => {
    mockApi({ results: mixedResults() })
    render(<App />)
    await scan('example.com')
    await screen.findByRole('img', { name: /SEO grade/ })

    const nav = screen.getByRole('navigation', { name: 'Report sections' })
    expect(within(nav).getByRole('button', { name: /Broken Links/ })).toHaveTextContent('1')
    expect(within(nav).getByRole('button', { name: /Thin Content/ })).toHaveTextContent('No issues')
  })

  it('celebrates a site with nothing to fix, even though info notices are present', async () => {
    mockApi({
      results: scanResults([issue('robots_txt_found', 'info', 'https://example.com/robots.txt')]),
      scan: { scan_id: 7, message: 'Scan completed', seo_grade: grade('A', 100) },
    })
    render(<App />)
    await scan('example.com')

    expect(await screen.findByText('No Issues Found!')).toBeInTheDocument()
    expect(screen.getByText('Issues').nextElementSibling).toHaveTextContent('0')
  })

  it('works when the response carries no grade', async () => {
    mockApi({ results: mixedResults(), scan: { scan_id: 7, message: 'ok' } })
    render(<App />)
    await scan('example.com')

    expect(await screen.findByText('Pages Analyzed')).toBeInTheDocument()
    expect(screen.queryByRole('img', { name: /SEO grade/ })).toBeNull()
  })

  it('clears the previous report when a new scan starts', async () => {
    mockApi({ results: mixedResults() })
    render(<App />)
    await scan('example.com')
    await screen.findByRole('img', { name: /SEO grade/ })

    const input = screen.getByLabelText('Website URL')
    await userEvent.setup().clear(input)
    await userEvent.setup().type(input, 'another.com')
    await userEvent.setup().click(screen.getByRole('button', { name: 'Scan site' }))

    expect(await screen.findByRole('img', { name: /SEO grade/ })).toBeInTheDocument()
    expect(screen.getAllByRole('img', { name: /SEO grade/ })).toHaveLength(1)
  })
})

describe('when something goes wrong', () => {
  it('explains that the backend cannot be reached', async () => {
    mockApi({ networkError: true })
    render(<App />)
    await scan('example.com')

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent("Can't reach the SEO Prism API")
    expect(alert).toHaveTextContent('http://localhost:8000')
    // still on the landing view, ready to try again
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Scan site' })).toBeEnabled()
  })

  it("shows the API's own reason for rejecting a scan", async () => {
    mockApi({ scanStatus: 400, scan: { detail: 'Invalid URL format' } })
    render(<App />)
    await scan('ftp://example.com')

    expect(await screen.findByRole('alert')).toHaveTextContent('Failed to start scan: Invalid URL format')
  })

  it('falls back to a generic message when the error has no detail', async () => {
    mockApi({ scanStatus: 500, scan: 'not json' })
    render(<App />)
    await scan('example.com')

    expect(await screen.findByRole('alert')).toHaveTextContent(/^Error: Failed to start scan$/)
  })
})
