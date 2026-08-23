import * as React from 'react'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'
  size?: 'default' | 'sm' | 'lg' | 'icon'
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'default', ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-semibold tracking-wide transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50'

    const variantStyles = {
      default: 'bg-linear-to-r from-primary-600 to-secondary-600 text-white shadow-lg shadow-secondary-600/25 hover:from-primary-500 hover:to-secondary-500 hover:shadow-lg hover:shadow-primary-500/30',
      destructive: 'bg-danger-600 text-white shadow-sm hover:bg-danger-500',
      outline: 'border border-white/15 bg-white/[0.04] text-foreground shadow-sm hover:border-white/25 hover:bg-white/[0.08]',
      secondary: 'border border-secondary-400/25 bg-secondary-500/15 text-secondary-200 hover:bg-secondary-500/25',
      ghost: 'text-muted-foreground hover:bg-white/[0.06] hover:text-foreground',
      link: 'text-primary-300 underline-offset-4 hover:underline',
    }
    
    const sizeStyles = {
      default: 'h-9 px-4 py-2',
      sm: 'h-8 rounded-md px-3 text-xs',
      lg: 'h-10 rounded-md px-8',
      icon: 'h-9 w-9',
    }
    
    return (
      <button
        className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className || ''}`}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = 'Button'

export { Button }