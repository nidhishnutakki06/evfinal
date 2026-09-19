# PHASE-01-REPORT

## Phase
Phase 1 — Domain Foundation + Deterministic Synthetic Data

## Status
PASS

## 1. What was implemented
Implemented the foundational domain model and deterministic synthetic-data layer required by later phases of the SH-305 Optimization + Simulation Engine. This included the canonical domain objects with physical validation, synthetic generation for realistic simulation start states, and comprehensive test suites ensuring validity and deterministic repetition using a fixed seed (42). All code strictly avoids implementation of simulation progression, energy calculation logic, and optimization strategies which are deferred to future phases.

## 2. Files created
- `src/sh305/__init__.py`
- `src/sh305/domain/__init__.py`
- `src/sh305/domain/enums.py`
- `src/sh305/domain/ev.py`
- `src/sh305/domain/station.py`
- `src/sh305/domain/building.py`
- `src/sh305/domain/environment.py`
- `src/sh305/domain/grid.py`
- `src/sh305/domain/simulation.py`
- `src/sh305/domain/system_state.py`
- `src/sh305/synthetic/__init__.py`
- `src/sh305/synthetic/vehicle_profiles.py`
- `src/sh305/synthetic/generator.py`
- `tests/__init__.py`
- `tests/test_profiles.py`
- `tests/test_domain_models.py`
- `tests/test_synthetic_data.py`
- `tests/test_determinism.py`
- `docs/implementation-notes/PHASE-01-REPORT.md`

## 3. Files modified
None (this was a clean foundational implementation, all files were newly created).

## 4. Domain models
- **EV**: Represents canonical Electric Vehicle with battery specs, current SOC, schedule bounds, and placeholders for downstream optimization features.
- **Station**: Models an individual charging point capable of hosting up to one EV. Exposes capacity and operational status.
- **Building**: Models static demand characteristics (AC, lights, lifts, appliances) and total required demand at an instant.
- **Solar**: Models renewable power sources on-site and its metrics like gross generation, usable, and excess power.
- **Environment**: Container for contextual simulation metadata such as weather and qualitative time-of-day.
- **Grid**: Represents grid connection constraints and capacity limitations, keeping track of active limits and safe modes.
- **Simulation**: Controls temporal bounds of the execution, maintaining tracking logic for start/end and progression states.
- **SystemState**: The central, canonical state holding collections of EVs, stations, environment instances, allocations, alerts, and other aggregate conditions.

## 5. State separation
The separation between `Simulation` and `Environment` represents a clear boundary between operational constraints and physical context. `Simulation` handles programmatic execution aspects (time tracking, start/end bounds, status). Conversely, `Environment` captures real-world physical constraints that affect optimization context (such as the qualitative effect of `WeatherCondition.SUNNY` vs `WeatherCondition.RAIN` or the qualitative phase of `TimeOfDay.MORNING`), keeping the physical state isolated from simulation-engine state variables.

## 6. Synthetic-data design
The synthetic layer generates an initialized `SystemState`. The profiles included are:
- `SUV`: 75.0 kWh battery, 420.0 km range, 3.3 kW - 11.0 kW charging.
- `Sedan`: 60.0 kWh battery, 380.0 km range, 3.3 kW - 11.0 kW charging.
- `Hatchback`: 35.0 kWh battery, 240.0 km range, 2.3 kW - 7.4 kW charging.
- `Scooter`: 3.5 kWh battery, 85.0 km range, 0.8 kW - 2.2 kW charging.
- `Bike`: 4.5 kWh battery, 110.0 km range, 1.0 kW - 3.3 kW charging.

*Note: These vehicle profiles are SYNTHETIC DEMO PARAMETERS only and are NOT manufacturer specifications nor sourced from real-world datasets.*

- **EV Generation**: Deterministically generates 8 default EVs of random types, diverse start SOC (15-80%), and feasible arrival/departure bounds.
- **Station Generation**: Deterministically generates 8 default stations across assorted common rates (22, 11, 7.4, 3.3 kW).
- **Building Baseline**: Static synthetic demand profile representing initial loads.
- **Solar Baseline**: Static solar output simulating starting point generation.
- **Environment Baseline**: Valid starting environment (e.g. SUNNY, MORNING).
- **Grid Baseline**: Valid starting safe grid configuration with normal active limits.
- **Random Seed**: Uses standard library `random` configured strictly to seed `42` to enforce deterministic, repeatable execution.

## 7. Validation rules
Basic physical checks implemented within Pydantic models:
- SoC limits bound strictly between 0 and 100.
- Battery and station capacities must be > 0.
- Charging rates strictly >= 0.
- Requested travel distances >= 0.
- Grid capacities and configured limits > 0.
- Energy and power values (demand components, grid contributions, solar generation) >= 0.

## 8. Phase boundary
Not implemented (deferred to subsequent phases):
- Simulation time-series updates or temporal loops.
- Dynamic building demand curve simulation.
- Real-time solar yield calculations.
- Optimization engine and algorithms.
- Feasibility scoring and priority assignments.
- Allocation distribution logic.
- Any 3D, frontend, or visual components.

## 9. Calculated-field boundary
**Source/Generated fields**: `ev_id`, `vehicle_type`, `battery_capacity_kwh`, `expected_range_km`, `current_soc`, `requested_travel_distance_km`, `arrival_time`, `departure_time`, `min_charging_rate_kw`, `max_charging_rate_kw`, `user_urgency`, `station_id`. These fields accurately hold generated information from the baseline.
**Calculated placeholders**: `target_soc`, `energy_required_kwh`, `time_remaining_hours`, `required_average_power_kw`, `priority_score`, `estimated_completion_time`, `estimated_soc_at_departure`, `deadline_status`, `physical_feasibility`, `current_allocation_feasibility`, `predictive_risk_flag`, `reason`, `grid_contribution_kw`, `solar_contribution_kw`. These fields are instantiated with valid, zeroed, or `None` defaults for safety and are not computed yet.

## 10. Tests executed
```bash
python -m pytest -v
```

## 11. Test results
```text
Total: 21
Passed: 21
Failed: 0
Skipped: 0
```

## 12. Sample generated data

**SystemState** (Top-level view):
```json
{
  "simulation": {
    "simulation_time": 0.0,
    "start_time": 0.0,
    "end_time": 24.0,
    "simulation_status": "IDLE"
  },
  "environment": {
    "weather": "SUNNY",
    "time_of_day": "MORNING"
  },
  "grid": {
    "configured_limit_kw": 500.0,
    "active_limit_kw": 500.0,
    "current_import_kw": 0.0,
    "available_capacity_kw": 500.0,
    "safety_state": "NORMAL",
    "emergency_mode": false
  },
  "building": {
    "ac_demand_kw": 45.5,
    "lights_demand_kw": 12.0,
    "lifts_demand_kw": 25.0,
    "appliances_demand_kw": 8.5,
    "total_demand_kw": 91.0
  },
  "solar": {
    "generation_kw": 35.0,
    "usable_solar_kw": 35.0,
    "excess_solar_kw": 0.0
  },
  "stations": [ ... ],
  "evs": [ ... ],
  "allocations": {
    "CS-01": 0.0,
    "CS-02": 0.0,
    "CS-03": 0.0,
    "CS-04": 0.0,
    "CS-05": 0.0,
    "CS-06": 0.0,
    "CS-07": 0.0,
    "CS-08": 0.0
  },
  "alerts": [],
  "strategy": "BALANCED",
  "emergency": false
}
```

**EV Sample**:
```json
{
  "ev_id": "EV-001",
  "vehicle_type": "SUV",
  "battery_capacity_kwh": 75.0,
  "expected_range_km": 420.0,
  "current_soc": 61.4,
  "requested_travel_distance_km": 123.7,
  "arrival_time": 9.43,
  "departure_time": 18.44,
  "min_charging_rate_kw": 3.3,
  "max_charging_rate_kw": 11.0,
  "current_charging_rate_kw": 0.0,
  "user_urgency": "LOW",
  "station_id": null,
  "grid_contribution_kw": 0.0,
  "solar_contribution_kw": 0.0,
  "target_soc": null,
  "energy_required_kwh": 0.0,
  "time_remaining_hours": 0.0,
  "required_average_power_kw": 0.0,
  "priority_score": 0.0,
  "estimated_completion_time": null,
  "estimated_soc_at_departure": null,
  "deadline_status": null,
  "physical_feasibility": null,
  "current_allocation_feasibility": null,
  "predictive_risk_flag": false,
  "reason": ""
}
```

**Station Sample**:
```json
{
  "station_id": "CS-01",
  "connected_ev_id": null,
  "station_capacity_kw": 22.0,
  "min_charging_rate_kw": 1.4,
  "max_charging_rate_kw": 22.0,
  "occupied": false,
  "current_allocated_power_kw": 0.0,
  "status": "AVAILABLE",
  "grid_contribution_kw": 0.0,
  "renewable_contribution_kw": 0.0
}
```

## 13. Design decisions
- Pydantic models are used natively for implicit serialization and structural guarantees alongside typed parameters for fields avoiding boilerplate getters/setters.
- Opted to separate the `SystemState` components explicitly as independent logical clusters.
- All generators take the seed on class instantiation ensuring multiple calls on the same state instance remain reproducible, avoiding unpredictable global randomness.

## 14. Limitations
- Generator produces a snapshot valid for only an instant in time without temporal fluidity.
- Static generation limits are simplified. True loads are inherently dynamic and heavily subject to variance outside standard deviation paths not modeled here.
- The `building` demand uses simplistic static summing missing typical industrial load fluctuations.

## 15. Next phase
Phase 2 should focus on introducing target SoC calculations, priority assessment, and mathematical feasibility calculations leveraging the now-available data foundation. Implementation of 24-hour simulation looping and dynamic allocations against real-time grid conditions should also be addressed.
