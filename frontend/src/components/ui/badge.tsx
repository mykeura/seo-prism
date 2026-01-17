import * as React from 'react'

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning'
}

function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  const variantStyles = {
    default: 'border-transparent bg-primary-600 text-primary-50 shadow hover:bg-primary-700',
    secondary: 'border-transparent bg-secondary-600 text-secondary-50 hover:bg-secondary-700',
    destructive: 'border-transparent bg-red-600 text-red-50 shadow hover:bg-red-700',
    outline: 'text-foreground',
    success: 'border-transparent bg-emerald-600 text-emerald-50 shadow hover:bg-emerald-700',
    warning: 'border-transparent bg-accent-600 text-accent-50 shadow hover:bg-accent-700',
  }
  
  return (
    <div
      className={`inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 ${variantStyles[variant]} ${className || ''}`}
      {...props}
    />
  )
}

export { Badge }