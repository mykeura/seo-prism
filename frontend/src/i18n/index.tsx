// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { en, type Translations } from './en'
import { es } from './es'

export type Language = 'en' | 'es'

const dictionaries: Record<Language, Translations> = { en, es }

export function detectLanguage(): Language {
  const browserLang = typeof navigator !== 'undefined' ? navigator.language : 'en'
  return browserLang.toLowerCase().startsWith('es') ? 'es' : 'en'
}

const LanguageContext = createContext<Translations>(en)

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language] = useState<Language>(detectLanguage)

  useEffect(() => {
    document.documentElement.lang = language
  }, [language])

  return (
    <LanguageContext.Provider value={dictionaries[language]}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useT(): Translations {
  return useContext(LanguageContext)
}
