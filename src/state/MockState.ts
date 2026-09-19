import type { SystemState } from '../types/SystemState';
import exampleStateJson from '../../contract/EXAMPLE_SYSTEM_STATE.json';
import { useDomainStore } from '../store';

// We assert the imported JSON strictly matches our TypeScript SystemState definition.
export const mockSystemState: SystemState = exampleStateJson as SystemState;

// Shared hook that connects the 3D scene directly to the live Zustand state,
// falling back to the static mock state during initial load.
export function useSystemState(): SystemState {
  const liveState = useDomainStore(state => state.systemState);
  return liveState || mockSystemState;
}
