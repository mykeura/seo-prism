// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { useId, type FormEvent } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCircleCheck, faGlobe, faTriangleExclamation } from '@fortawesome/free-solid-svg-icons'
import { Button } from './ui/button'
import { cn } from '../lib/utils'
import { useT } from '../i18n'

interface ScanFormProps {
  url: string
  onUrlChange: (url: string) => void
  onSubmit: (e: FormEvent) => void
  loading: boolean
  message: string | null
  error: string | null
  /** 'hero' on the landing view, 'compact' once results are on screen. */
  variant?: 'hero' | 'compact'
}

export function ScanForm({
  url,
  onUrlChange,
  onSubmit,
  loading,
  message,
  error,
  variant = 'hero',
}: ScanFormProps) {
  const t = useT()
  const inputId = useId()
  const hero = variant === 'hero'

  return (
    <div className={cn('mx-auto w-full', hero ? 'mt-10 max-w-2xl' : 'max-w-none')}>
      <form onSubmit={onSubmit} aria-busy={loading} noValidate>
        <div
          className={cn(
            'flex items-center gap-3 rounded-2xl border border-white/10 bg-card/70 pl-4 backdrop-blur-md transition-all duration-200',
            'focus-within:border-primary-400/50 focus-within:ring-4 focus-within:ring-primary-400/15',
            hero
              ? 'p-2 shadow-[0_24px_60px_-24px_rgba(99,102,241,0.45)]'
              : 'p-1.5 shadow-[0_12px_32px_-20px_rgba(0,0,0,0.8)]',
          )}
        >
          <FontAwesomeIcon icon={faGlobe} className="shrink-0 text-muted-foreground" aria-hidden="true" />
          <label htmlFor={inputId} className="sr-only">
            {t.form.inputLabel}
          </label>
          <input
            id={inputId}
            type="text"
            inputMode="url"
            autoComplete="url"
            autoCapitalize="none"
            spellCheck={false}
            value={url}
            onChange={(e) => onUrlChange(e.target.value)}
            placeholder={t.form.placeholder}
            disabled={loading}
            className={cn(
              'min-w-0 flex-1 bg-transparent font-mono outline-none placeholder:text-muted-foreground/55 disabled:cursor-not-allowed disabled:opacity-60',
              hero ? 'h-12 text-[15px]' : 'h-10 text-sm',
            )}
          />
          <Button
            type="submit"
            size={hero ? 'lg' : 'default'}
            disabled={loading || !url.trim()}
            className={hero ? '' : 'h-10 rounded-xl px-5'}
          >
            {loading ? t.form.scanning : t.form.scanAction}
          </Button>
        </div>

        {loading && (
          <div className="mt-4" role="status">
            <div className="scan-progress" />
            <p className="mt-3 text-center text-sm text-muted-foreground">{t.form.scanningHint}</p>
          </div>
        )}
      </form>

      {message && !loading && (
        <p className="mt-4 flex items-center justify-center gap-2 text-sm text-muted-foreground">
          <FontAwesomeIcon icon={faCircleCheck} className="text-success-400" aria-hidden="true" />
          {message}
        </p>
      )}

      {error && (
        <div
          role="alert"
          className="mt-4 flex items-start gap-3 rounded-xl border border-danger-400/25 bg-danger-500/10 px-4 py-3 text-sm text-danger-200"
        >
          <FontAwesomeIcon icon={faTriangleExclamation} className="mt-0.5 shrink-0 text-danger-300" aria-hidden="true" />
          <span>
            {t.form.errorPrefix}: {error}
          </span>
        </div>
      )}
    </div>
  )
}
