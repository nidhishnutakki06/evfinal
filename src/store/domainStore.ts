import { create } from 'zustand';
import type { SystemState } from '@/types/system.types';
import type { WebSocketConnectionState } from '@/services/ws/client';

interface DomainState {
  systemState: SystemState | null;
  connectionStatus: WebSocketConnectionState;
  lastUpdated: number | null;
  setSystemState: (state: SystemState) => void;
  setConnectionStatus: (status: WebSocketConnectionState) => void;
  clearSystemState: () => void;
}

export const useDomainStore = create<DomainState>((set) => ({
  systemState: null,
  connectionStatus: 'disconnected',
  lastUpdated: null,
  setSystemState: (state: SystemState) => set({ systemState: state, lastUpdated: Date.now() }),
  setConnectionStatus: (status: WebSocketConnectionState) => set({ connectionStatus: status }),
  clearSystemState: () => set({ systemState: null, lastUpdated: null }),
}));
