import type { ReactNode } from "react"
import { useUIStore } from "@/store"
import { Menu } from "lucide-react"

interface DashboardLayoutProps {
  children: ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { isSidebarOpen, toggleSidebar } = useUIStore()

  return (
    <div className="flex h-screen w-full flex-col overflow-hidden bg-background text-foreground">
      {/* Header Area */}
      <header className="flex h-16 shrink-0 items-center justify-between border-b px-4">
        <div className="flex items-center gap-4">
          <button
            onClick={toggleSidebar}
            className="rounded-md p-2 hover:bg-surface focus:outline-none focus:ring-2 focus:ring-ring"
            aria-label="Toggle Sidebar"
          >
            <Menu className="h-5 w-5" />
          </button>
          <h1 className="text-lg font-semibold tracking-tight">SH-305 Dashboard</h1>
        </div>
        <div className="flex items-center gap-4">
          {/* Future global controls / status */}
          <div className="text-sm text-muted-foreground">System Status: Standby</div>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar Area (Future Detail Panels / EV Lists) */}
        {isSidebarOpen && (
          <aside className="w-80 shrink-0 border-r bg-surface/50 p-4 overflow-y-auto">
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Control Panel
            </h2>
            <div className="rounded-md border border-dashed border-muted-foreground/30 p-4 text-center text-sm text-muted-foreground">
              Future Detail Panel Area
            </div>
          </aside>
        )}

        {/* Primary Content (Future 3D / Metrics) */}
        <main className="flex-1 overflow-auto p-4">
          {children}
        </main>
      </div>
    </div>
  )
}
