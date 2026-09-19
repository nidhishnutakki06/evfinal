import type { SystemState } from "@/types/system.types";
import exampleData from "../../../contract/EXAMPLE_SYSTEM_STATE.json";

// We assert the imported JSON matches our canonical SystemState interface.
// This ensures that if the schema diverges significantly from the mock data, TypeScript will flag it.
export const mockSystemState: SystemState = exampleData as SystemState;
