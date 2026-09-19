import { apiClient } from "./client";
import type { SystemState } from "@/types/system.types";

export const stateApi = {
  getHealth: () => apiClient.get<{ status: string }>("/health"),
  getState: () => apiClient.get<SystemState>("/state"),
};
