import type { SystemState } from '../types/SystemState';
import exampleStateJson from '../../contract/EXAMPLE_SYSTEM_STATE.json';

// We assert the imported JSON strictly matches our TypeScript SystemState definition.
export const mockSystemState: SystemState = exampleStateJson as SystemState;

// Simple store/hook placeholder for the 3D application to consume later
export function useSystemState(): SystemState {
  return mockSystemState;
}
