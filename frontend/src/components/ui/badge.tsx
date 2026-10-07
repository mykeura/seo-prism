// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import * as React from 'react'

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning'
}

function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  const variantStyles = {
    default: 'border-primary-400/25 bg-primary-500/10 text-primary-300',
    secondary: 'border-secondary-400/25 bg-secondary-500/10 text-secondary-300',
    destructive: 'border-danger-400/30 bg-danger-500/10 text-danger-300',
    outline: 'border-border bg-white/[0.03] text-muted-foreground',
    success: 'border-success-400/25 bg-success-500/10 text-success-300',
    warning: 'border-warning-400/30 bg-warning-500/10 text-warning-300',
  }

  return (
    <div
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wider transition-colors focus:outline-none focus:ring-2 focus:ring-ring/60 focus:ring-offset-2 focus:ring-offset-background ${variantStyles[variant]} ${className || ''}`}
      {...props}
    />
  )
}

export { Badge }