import { create } from 'zustand'

interface UIState {
  isSidebarOpen: boolean
  toggleSidebar: () => void
  activePanel: string | null
  setActivePanel: (panel: string | null) => void
}

// Minimal UI state foundation for Zustand
export const useUIStore = create<UIState>((set) => ({
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  activePanel: null,
  setActivePanel: (panel) => set({ activePanel: panel }),
}))

export { useDomainStore } from './domainStore'
