import * as React from 'react'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'
  size?: 'default' | 'sm' | 'lg' | 'icon'
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'default', ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50'
    
    const variantStyles = {
      default: 'bg-primary-600 text-primary-50 shadow hover:bg-primary-700',
      destructive: 'bg-red-600 text-red-50 shadow-sm hover:bg-red-700',
      outline: 'border border-border bg-background shadow-sm hover:bg-accent-600 hover:text-accent-50',
      secondary: 'bg-secondary-600 text-secondary-50 shadow-sm hover:bg-secondary-700',
      ghost: 'hover:bg-accent-600 hover:text-accent-50',
      link: 'text-primary-600 underline-offset-4 hover:underline',
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