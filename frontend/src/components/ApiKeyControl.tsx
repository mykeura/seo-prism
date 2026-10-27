// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { useEffect, useId, useState } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faKey } from '@fortawesome/free-solid-svg-icons'
import { Button } from './ui/button'
import { useT } from '../i18n'
import {
  API_KEY_REQUIRED_EVENT,
  clearApiKey,
  getApiKey,
  setApiKey,
} from '../lib/api'

/**
 * API-key control for deployments protected with SEO_PRISM_API_KEY.
 * The value lives in sessionStorage only; 401 responses open this panel.
 */
export function ApiKeyControl() {
  const t = useT()
  const panelId = useId()
  const [open, setOpen] = useState(false)
  const [draft, setDraft] = useState('')
  const [hasKey, setHasKey] = useState(() => Boolean(getApiKey()))

  useEffect(() => {
    const reveal = () => {
      setDraft(getApiKey())
      setHasKey(Boolean(getApiKey()))
      setOpen(true)
    }
    window.addEventListener(API_KEY_REQUIRED_EVENT, reveal)
    return () => window.removeEventListener(API_KEY_REQUIRED_EVENT, reveal)
  }, [])

  const toggle = () => {
    setDraft(getApiKey())
    setOpen((current) => !current)
  }

  const save = () => {
    setApiKey(draft)
    setHasKey(Boolean(getApiKey()))
    setOpen(false)
  }

  const clear = () => {
    clearApiKey()
    setDraft('')
    setHasKey(false)
  }

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="sm"
        onClick={toggle}
        aria-expanded={open}
        aria-controls={panelId}
      >
        <FontAwesomeIcon icon={faKey} aria-hidden="true" />
        {hasKey ? t.apiKey.configured : t.apiKey.button}
      </Button>

      {open && (
        <div
          id={panelId}
          className="absolute right-0 z-20 mt-2 w-80 rounded-xl border border-white/10 bg-card p-4 text-left shadow-2xl"
        >
          <label
            htmlFor={`${panelId}-input`}
            className="block text-sm font-medium text-foreground"
          >
            {t.apiKey.title}
          </label>
          <input
            id={`${panelId}-input`}
            type="password"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder={t.apiKey.placeholder}
            autoComplete="off"
            spellCheck={false}
            className="mt-2 w-full rounded-lg border border-white/10 bg-background px-3 py-2 font-mono text-sm outline-none transition-colors focus:border-primary-400/50"
          />
          <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
            {t.apiKey.description}
          </p>
          <div className="mt-3 flex justify-end gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={clear}
              disabled={!hasKey && !draft}
            >
              {t.apiKey.clear}
            </Button>
            <Button size="sm" onClick={save}>
              {t.apiKey.save}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
