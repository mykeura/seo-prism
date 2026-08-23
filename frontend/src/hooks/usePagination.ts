import { useState } from 'react'

export function usePagination(initial = 5, step = 10) {
  const [visible, setVisible] = useState(initial)

  const loadMore = () => setVisible(prev => prev + step)
  const reset = () => setVisible(initial)
  const hasMore = (total: number) => total > visible

  return { visible, hasMore, loadMore, reset }
}
