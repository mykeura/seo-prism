interface ShowMoreButtonProps {
  visible: number
  total: number
  label?: string
  onClick: () => void
}

export function ShowMoreButton({ visible, total, label = 'items', onClick }: ShowMoreButtonProps) {
  return (
    <button
      onClick={onClick}
      className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2 text-muted-foreground"
    >
      Showing {visible} of {total} {label}.
    </button>
  )
}
