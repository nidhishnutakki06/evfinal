# API Contract

Defines the external schema for SH-305.

### SystemState
- **simulation**: simulation state `{"current_time": number, "start": number, "end": number, "status": string}`
- **strategy**: `{"active_strategy": string}`
- **emergency**: `{"active": boolean}`
- **building**: `{"total_building_demand": number}`
- **allocations**: Array of `{"station_id": string, "allocated_power": number}`
- **evs**: Array of EV objects with fields like `ev_id`, `vehicle_type`, `urgency`, `battery_capacity`, `range`, `current_soc`, `requested_travel_distance`, `arrival`, `departure`, `minimum_rate`, `maximum_rate`, `current_rate`, `energy_required`, `time_remaining`, `required_average_power`, `estimated_completion`, `a3_risk`, `a2_reason`.
