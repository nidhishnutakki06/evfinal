import { useSyncExternalStore } from 'react'

export type EntityType = 'building' | 'station' | 'ev' | 'solar' | 'grid' | 'wire' | null

export interface Selection {
  type: EntityType
  id: string | null
}

let currentSelection: Selection = { type: null, id: null }
const listeners = new Set<() => void>()

export const SelectionState = {
  getSnapshot: () => currentSelection,
  subscribe: (listener: () => void) => {
    listeners.add(listener)
    return () => listeners.delete(listener)
  },
  select: (type: EntityType, id: string | null) => {
    if (currentSelection.type !== type || currentSelection.id !== id) {
      currentSelection = { type, id }
      listeners.forEach((l) => l())
    }
  },
  clear: () => {
    if (currentSelection.type !== null || currentSelection.id !== null) {
      currentSelection = { type: null, id: null }
      listeners.forEach((l) => l())
    }
  }
}

export function useSelection() {
  return useSyncExternalStore(SelectionState.subscribe, SelectionState.getSnapshot)
}
