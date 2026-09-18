import { apiClient } from "./client";
import type { SystemState } from "@/types/system.types";
import type {
  BuildingDemandRequest,
  GridLimitRequest,
  WeatherRequest,
  StrategyRequest,
  SpawnEVRequest
} from "@/types/control.types";

export const controlsApi = {
  // Simulation Lifecycle
  startSimulation: () => apiClient.post<SystemState>("/simulation/start"),
  pauseSimulation: () => apiClient.post<SystemState>("/simulation/pause"),
  resetSimulation: () => apiClient.post<SystemState>("/simulation/reset"),

  // Configuration & Control Mutations
  setBuildingDemand: (data: BuildingDemandRequest) => apiClient.post<SystemState>("/control/building-demand", data),
  setGridLimit: (data: GridLimitRequest) => apiClient.post<SystemState>("/control/grid-limit", data),
  setWeather: (data: WeatherRequest) => apiClient.post<SystemState>("/control/weather", data),
  setStrategy: (data: StrategyRequest) => apiClient.post<SystemState>("/control/strategy", data),

  // EV Spawning Mechanics
  spawnEV: (data: SpawnEVRequest) => apiClient.post<SystemState>("/control/spawn-ev", data),
  spawnUrgentEV: (data: SpawnEVRequest) => apiClient.post<SystemState>("/control/spawn-urgent-ev", data),

  // Emergency Intervention
  activateEmergency: () => apiClient.post<SystemState>("/control/emergency/activate"),
  restoreEmergency: () => apiClient.post<SystemState>("/control/emergency/restore"),
};
