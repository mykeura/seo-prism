import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faChevronDown } from '@fortawesome/free-solid-svg-icons'
import { useT } from '../i18n'

interface ShowMoreButtonProps {
  visible: number
  total: number
  label?: string
  onClick: () => void
}

export function ShowMoreButton({ visible, total, label, onClick }: ShowMoreButtonProps) {
  const t = useT()
  return (
    <button
      onClick={onClick}
      className="group inline-flex h-9 items-center justify-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-5 text-sm font-medium text-muted-foreground transition-all duration-200 hover:border-primary-400/30 hover:bg-primary-500/10 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50"
    >
      {t.common.showingOf(visible, total, label ?? t.common.items)}
      <FontAwesomeIcon icon={faChevronDown} className="text-xs transition-transform duration-200 group-hover:translate-y-0.5" />
    </button>
  )
}
