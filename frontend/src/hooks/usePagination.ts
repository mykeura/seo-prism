// SPDX-License-Identifier: AGPL-3.0-only
// SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import { useState } from 'react'

export function usePagination(initial = 5, step = 10) {
  const [visible, setVisible] = useState(initial)

  const loadMore = () => setVisible(prev => prev + step)
  const reset = () => setVisible(initial)
  const hasMore = (total: number) => total > visible

  return { visible, hasMore, loadMore, reset }
}
