import type { StrategyType } from "./system.types";

export interface BuildingDemandRequest {
  ac: number;
  lights: number;
  lifts: number;
  appliances: number;
}

export interface GridLimitRequest {
  limit: number;
}

export interface WeatherRequest {
  weather: string;
}

export interface StrategyRequest {
  active_strategy: StrategyType;
}

export interface SpawnEVRequest {
  ev_id: string;
  vehicle_type: string;
  battery_capacity: number;
  target_soc: number;
  requested_travel_distance?: number;
  arrival: number;
  departure: number;
  minimum_rate?: number;
  maximum_rate: number;
  station_id?: string | null;
}
