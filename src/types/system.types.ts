export type AlertCategory = "A3_PREDICTIVE_RISK" | "EMERGENCY_EVENT" | "SAFETY_EVENT";

export interface Alert {
  alert_id: string;
  type: AlertCategory;
  message: string;
  timestamp: number;
  severity: string;
}

export interface Allocation {
  ev_id: string;
  allocated_rate?: number;
  allocation_status?: string;
  grid_contribution?: number;
  solar_contribution?: number;
}

export interface Building {
  ac_demand?: number;
  lights_demand?: number;
  lifts_demand?: number;
  appliances_demand?: number;
  total_building_demand?: number;
}

export interface EV {
  ev_id: string;
  vehicle_type: string;
  battery_capacity: number;
  range?: number;
  current_soc: number;
  target_soc: number;
  requested_travel_distance?: number;
  arrival: number;
  departure: number;
  minimum_rate?: number;
  maximum_rate: number;
  current_rate?: number;
  energy_required?: number;
  time_remaining?: number;
  required_average_power?: number;
  urgency?: string;
  priority_score?: number;
  estimated_completion?: number;
  estimated_soc_at_departure?: number;
  deadline_status?: string;
  physical_feasibility?: boolean;
  current_allocation_feasibility?: boolean;
  a3_risk?: string;
  a2_reason?: string;
  grid_contribution?: number;
  solar_contribution?: number;
  station_id?: string | null;
}

export interface Emergency {
  emergency_active_state?: boolean;
  emergency_limit: number;
}

export interface Environment {
  weather?: string;
  time_of_day?: string;
}

export interface Grid {
  configured_limit: number;
  active_limit: number;
  grid_import?: number;
  available_capacity?: number;
  safety_state?: string;
}

export interface Simulation {
  simulation_time?: number;
  is_running?: boolean;
  timestep?: number;
}

export interface Solar {
  generation?: number;
  usable_solar?: number;
  excess_solar?: number;
}

export interface Station {
  station_id: string;
  occupancy?: boolean;
  connected_ev_id?: string | null;
  capacity: number;
  minimum_charging_rate?: number;
  maximum_charging_rate: number;
  allocated_power?: number;
  status?: string;
}

export type StrategyType = "DEADLINE_FIRST" | "SOLAR_FIRST" | "GRID_SAFETY_FIRST";

export interface Strategy {
  active_strategy?: StrategyType;
}

export interface SystemState {
  simulation: Simulation;
  environment: Environment;
  grid: Grid;
  building: Building;
  solar: Solar;
  stations: Station[];
  evs: EV[];
  allocations: Allocation[];
  alerts: Alert[];
  strategy: Strategy;
  emergency: Emergency;
}
