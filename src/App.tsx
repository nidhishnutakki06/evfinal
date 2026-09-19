import { useEffect } from "react"
import { DashboardShell } from "@/components/dashboard/DashboardShell"
import { wsClient } from "@/services/ws/client"
import { stateApi } from "@/services/api/state"
import { useDomainStore } from "@/store"
import { env } from "@/config/env"
import type { SystemState } from "@/types/system.types"
import exampleStateRaw from "../contract/EXAMPLE_SYSTEM_STATE.json"

function App() {
  const setSystemState = useDomainStore(state => state.setSystemState)
  const setConnectionStatus = useDomainStore(state => state.setConnectionStatus)

  useEffect(() => {
    let mounted = true

    const initialize = async () => {
      if (env.IS_DEV_PREVIEW) {
        console.info("[DEV PREVIEW] Bypassing REST and WebSocket. Loading example state.");
        setSystemState(exampleStateRaw as unknown as SystemState);
        setConnectionStatus('disconnected'); // Controlled explicitly by the badge indicator
        return;
      }

      // 1. Fetch initial state
      try {
        const state = await stateApi.getState()
        if (mounted && state) {
          setSystemState(state)
        }
      } catch (err) {
        console.error("Failed to fetch initial SystemState from REST:", err)
      }

      // 2. Connect WebSocket for realtime snapshots AFTER REST completes
      if (mounted) {
        wsClient.connect()
      }
    }

    initialize()

    const unsubscribeState = wsClient.onStateChange((status) => {
      if (mounted) setConnectionStatus(status)
    })

    const unsubscribeMessage = wsClient.subscribe((data) => {
      if (mounted && data) {
        setSystemState(data)
      }
    })

    // 3. Cleanup on unmount
    return () => {
      mounted = false
      unsubscribeState()
      unsubscribeMessage()
      wsClient.disconnect()
    }
  }, [setSystemState, setConnectionStatus])

  return <DashboardShell />
}

export default App
