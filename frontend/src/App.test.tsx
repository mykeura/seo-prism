// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { LanguageProvider } from './i18n'
import { clearApiKey, setApiKey } from './lib/api'
import { grade, issue, scanResults } from './test/fixtures'
import type { ScanResults } from './types'

afterEach(() => clearApiKey())

function mockApi(options: {
  results?: ScanResults
  scan?: unknown
  scanStatus?: number
  scans?: unknown
  scansStatus?: number
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
    if (url.endsWith('/scans')) {
      return json(options.scans ?? { scans: [] }, options.scansStatus ?? 200)
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

const historyResponse = {
  scans: [
    {
      scan_id: 3,
      url: 'https://old.example.com',
      scan_date: '2026-10-01T09:30:00',
      grade_letter: 'C',
      grade_score: 61,
      total_issues: 9,
    },
    {
      scan_id: 1,
      url: 'https://first.example.com',
      scan_date: '2026-09-20T18:00:00',
      grade_letter: 'A',
      grade_score: 98,
      total_issues: 0,
    },
  ],
}

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

  it('sends the API key from sessionStorage on every request', async () => {
    setApiKey('sekrit')
    const fetchMock = mockApi({ results: mixedResults() })
    render(<App />)

    await scan('example.com')
    await screen.findByRole('img', { name: /SEO grade/ })

    const [scanCall, resultsCall] = fetchMock.mock.calls
    expect(new Headers((scanCall[1] as RequestInit).headers).get('X-API-Key')).toBe('sekrit')
    expect(new Headers((resultsCall[1] as RequestInit).headers).get('X-API-Key')).toBe('sekrit')
  })

  it('opens the API key panel and explains a 401', async () => {
    mockApi({ scanStatus: 401, scan: { detail: 'Unauthorized' } })
    render(<App />)

    await scan('example.com')

    expect(await screen.findByRole('alert')).toHaveTextContent(/requires an API key/)
    expect(screen.getByLabelText('API key')).toBeInTheDocument()
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

describe('scan history', () => {
  it('fetches the history only when the panel opens and lists each scan', async () => {
    const fetchMock = mockApi({ scans: historyResponse })
    render(<App />)
    expect(fetchMock).not.toHaveBeenCalled()

    await userEvent.setup().click(screen.getByRole('button', { name: 'Scan history' }))

    expect(await screen.findByText('https://old.example.com')).toBeInTheDocument()
    expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/scans$/)
    const row = screen.getByRole('button', { name: /old\.example\.com/ })
    expect(within(row).getByText('C')).toBeInTheDocument()
    expect(within(row).getByText('9')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /first\.example\.com/ })).toBeInTheDocument()
  })

  it('refreshes the history when a scan finishes with the panel open', async () => {
    const finishedScan = {
      scan_id: 7,
      url: 'https://example.com',
      scan_date: '2026-10-27T18:00:00+00:00',
      grade_letter: 'B',
      grade_score: 84,
      total_issues: 4,
    }
    let scansCalls = 0
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input)
        const json = (body: unknown, status = 200) =>
          new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
        if (url.endsWith('/scans')) {
          scansCalls += 1
          // The first load predates the scan; the refetch carries its row.
          return json(scansCalls === 1 ? historyResponse : { scans: [finishedScan, ...historyResponse.scans] })
        }
        if (url.endsWith('/scan')) {
          return json({ scan_id: 7, message: 'Scan completed', seo_grade: grade('B', 84) })
        }
        if (/\/results(\/\d+)?$/.test(url)) return json(mixedResults())
        throw new Error(`unexpected request: ${url}`)
      }),
    )
    render(<App />)
    const user = userEvent.setup()

    await user.click(screen.getByRole('button', { name: 'Scan history' }))
    expect(await screen.findByText('https://old.example.com')).toBeInTheDocument()
    expect(scansCalls).toBe(1)

    await scan('example.com')

    const panel = document.getElementById('scan-history') as HTMLElement
    expect(await within(panel).findByText('https://example.com')).toBeInTheDocument()
    expect(scansCalls).toBe(2)
    expect(within(panel).getByText('https://old.example.com')).toBeInTheDocument()
  })

  it('shows an empty state before the first scan exists', async () => {
    mockApi({ scans: { scans: [] } })
    render(<App />)

    await userEvent.setup().click(screen.getByRole('button', { name: 'Scan history' }))

    expect(await screen.findByText('No scans yet')).toBeInTheDocument()
    expect(screen.getByText('Run your first scan and it will appear here.')).toBeInTheDocument()
  })

  it('reports a failed request and retries it', async () => {
    const fetchMock = mockApi({ scans: { detail: 'db locked' }, scansStatus: 500 })
    render(<App />)
    const user = userEvent.setup()
    await user.click(screen.getByRole('button', { name: 'Scan history' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Failed to load scan history: db locked')

    await user.click(screen.getByRole('button', { name: 'Retry' }))
    expect(await screen.findByRole('alert')).toBeInTheDocument()
    const scansCalls = fetchMock.mock.calls.filter(([url]) => String(url).endsWith('/scans'))
    expect(scansCalls).toHaveLength(2)
  })

  it('explains that the API cannot be reached', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        throw new TypeError('Failed to fetch')
      }),
    )
    render(<App />)

    await userEvent.setup().click(screen.getByRole('button', { name: 'Scan history' }))

    expect(await screen.findByRole('alert')).toHaveTextContent("Can't reach the SEO Prism API")
  })

  it('reopens a stored report through the existing results flow', async () => {
    const fetchMock = mockApi({ scans: historyResponse, results: mixedResults() })
    render(<App />)
    const user = userEvent.setup()
    await user.click(screen.getByRole('button', { name: 'Scan history' }))

    await user.click(await screen.findByRole('button', { name: /old\.example\.com/ }))

    expect(await screen.findByRole('img', { name: 'SEO grade C, 61 out of 100' })).toBeInTheDocument()
    expect(String(fetchMock.mock.calls[1][0])).toMatch(/\/results\/3$/)
    // the form input follows the reopened report's own URL
    expect(screen.getByLabelText('Website URL')).toHaveValue('https://example.com')
  })

  it('surfaces a failure when the stored report cannot be fetched', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input)
        const json = (body: unknown, status = 200) =>
          new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
        if (url.endsWith('/scans')) return json(historyResponse)
        if (url.endsWith('/results/3')) return json({ detail: 'Scan not found' }, 404)
        throw new Error(`unexpected request: ${url}`)
      }),
    )
    render(<App />)
    const user = userEvent.setup()
    await user.click(screen.getByRole('button', { name: 'Scan history' }))

    await user.click(await screen.findByRole('button', { name: /old\.example\.com/ }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Failed to get results')
  })
})

describe('csv export', () => {
  function stubBlobUrl() {
    const blobs: Blob[] = []
    const downloads: HTMLAnchorElement[] = []
    const url = URL as unknown as Record<'createObjectURL' | 'revokeObjectURL', unknown>
    const originalCreate = url.createObjectURL
    const originalRevoke = url.revokeObjectURL
    url.createObjectURL = (blob: Blob) => {
      blobs.push(blob)
      return 'blob:mock'
    }
    url.revokeObjectURL = () => {}
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (this: HTMLAnchorElement) {
      downloads.push(this)
    })
    return {
      blobs,
      downloads,
      restore: () => {
        url.createObjectURL = originalCreate
        url.revokeObjectURL = originalRevoke
        vi.mocked(HTMLAnchorElement.prototype.click).mockRestore()
      },
    }
  }

  let stub: ReturnType<typeof stubBlobUrl>
  afterEach(() => stub.restore())

  it('downloads the active section, following the section switch', async () => {
    stub = stubBlobUrl()
    mockApi({ results: mixedResults() })
    render(<App />)
    await scan('example.com')
    await screen.findByRole('img', { name: /SEO grade/ })

    // the report opens on Header Analysis (its missing H1 is the top severity)
    await userEvent.setup().click(screen.getByRole('button', { name: 'Export CSV' }))
    expect(stub.blobs).toHaveLength(1)
    expect(await stub.blobs[0].text()).toBe(
      [
        '"issue_type","url","source_page","severity","description"',
        '"missing_h1","https://example.com/a","https://example.com/a","high","missing_h1 on https://example.com/a"',
      ].join('\n'),
    )
    expect(stub.downloads[0].download).toBe('seo-prism-headerAnalysis-7.csv')

    const nav = screen.getByRole('navigation', { name: 'Report sections' })
    await userEvent.setup().click(within(nav).getByRole('button', { name: /Broken Links/ }))
    await userEvent.setup().click(screen.getByRole('button', { name: 'Export CSV' }))
    const csv = await stub.blobs[1].text()
    expect(csv).toContain('"broken_link","https://example.com/gone","https://example.com/","medium"')
    expect(stub.downloads[1].download).toBe('seo-prism-brokenLinks-7.csv')
  })

  it('quotes fields so commas and quotes survive the round trip', async () => {
    stub = stubBlobUrl()
    mockApi({
      results: scanResults([
        issue('missing_title', 'high', 'https://example.com/a,b', {
          description: 'says "hello", loudly',
        }),
      ]),
    })
    render(<App />)
    await scan('example.com')
    await screen.findByRole('img', { name: /SEO grade/ })

    await userEvent.setup().click(screen.getByRole('button', { name: 'Export CSV' }))

    expect(await stub.blobs[0].text()).toBe(
      [
        '"issue_type","url","source_page","severity","description"',
        '"missing_title","https://example.com/a,b","https://example.com/a,b","high","says ""hello"", loudly"',
      ].join('\n'),
    )
  })

  it('stays disabled for a section without issues', async () => {
    stub = stubBlobUrl()
    mockApi({ results: mixedResults() })
    render(<App />)
    await scan('example.com')
    await screen.findByRole('img', { name: /SEO grade/ })

    const nav = screen.getByRole('navigation', { name: 'Report sections' })
    await userEvent.setup().click(within(nav).getByRole('button', { name: /Thin Content/ }))

    expect(screen.getByRole('button', { name: 'Export CSV' })).toBeDisabled()
    expect(stub.blobs).toHaveLength(0)
  })
})
