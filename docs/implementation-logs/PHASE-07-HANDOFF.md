# Phase 7 Handoff

Status: PASS

This document outlines the final integration surface and boundaries for integrating Person 3's engine into the main SH-305 backend.

## Public Engine Interfaces

The engine exposes the following exact callable interfaces, primarily located in `sh305.engine.controller`, `sh305.engine.simulation`, and `sh305.synthetic.generator`.

### Initialization & Simulation
- **`SyntheticDataGenerator.generate_initial_system_state(ev_count: int = 8, station_count: int = 8) -> SystemState`**
  - **Input**: Optional counts for EVs and stations.
  - **Output**: The fully initialized canonical `SystemState`.
  - **Recomputation**: No immediate priority calculation until `_recompute()` or `step_simulation()` is called.
  - **Errors**: Standard `pydantic` validation exceptions if underlying models fail bounds.
- **`step_simulation(state: SystemState, step_hours: float = 0.25, weights: WeightConfig = None) -> None`**
  - **Input**: The active `SystemState`, simulation step size, and optional `WeightConfig`.
  - **Output**: None (Mutates `SystemState` in-place).
  - **State Modified**: Simulation time advances, EV SoC is updated based on previous allocation, environment conditions (weather, solar, building) automatically iterate deterministically. EVs arrive/depart. Recomputes everything.
  - **Recomputation**: Yes (Internal `update_state_allocation()` called).
  - **Errors**: None expected from well-formed data.

### Direct Allocation
- **`update_state_allocation(state: SystemState, weights: WeightConfig, control_interval_hours: float = 0.25, reserve_percent: float = 10.0) -> None`** (Also aliased by `_recompute` in the controller)
  - **Input**: The `SystemState`, explicit weights, and interval.
  - **Output**: None (Mutates `SystemState` in-place).
  - **State Modified**: Updates EV target metrics, priority scores, prediction flags (A3), explanation reasons (A2), and enforces final dynamic grid/station power dispatch limits.
  - **Recomputation**: Immediate full allocation.

### A1–A5 Control Events
All control events immediately trigger a full pipeline recomputation and modify the `SystemState` in place.
- **`apply_building_demand_delta(state: SystemState, delta_kw: float, step_hours: float = 0.25, weights: WeightConfig = None) -> None`**
- **`apply_grid_limit_delta(state: SystemState, delta_kw: float, step_hours: float = 0.25, weights: WeightConfig = None) -> None`**
- **`change_weather(state: SystemState, weather: WeatherCondition, step_hours: float = 0.25, weights: WeightConfig = None) -> None`**
- **`spawn_ev(state: SystemState, urgency: UserUrgency = UserUrgency.MEDIUM, step_hours: float = 0.25, weights: WeightConfig = None) -> EV`**
  - **Output**: Returns the newly spawned `EV` instance in addition to modifying `state`.
  - **Errors**: Raises `RuntimeError` if no available stations exist.
- **`spawn_urgent_ev(state: SystemState, step_hours: float = 0.25, weights: WeightConfig = None) -> EV`**
- **`set_strategy(state: SystemState, strategy: str, step_hours: float = 0.25) -> None`**
  - **Input**: `strategy` must be one of `"DEADLINE_FIRST"`, `"SOLAR_FIRST"`, or `"GRID_SAFETY_FIRST"`.
  - **Errors**: Raises `ValueError` if the strategy name is unrecognized.
- **`activate_emergency(state: SystemState, reduction_fraction: float = 0.40, step_hours: float = 0.25, weights: WeightConfig = None) -> None`**
- **`restore_grid(state: SystemState, step_hours: float = 0.25, weights: WeightConfig = None) -> None`**

## Example Call Flow
```python
from sh305.synthetic.generator import SyntheticDataGenerator
from sh305.engine.simulation import step_simulation
from sh305.engine.controller import apply_building_demand_delta

# 1. Initialize
generator = SyntheticDataGenerator(seed=42)
state = generator.generate_initial_system_state()

# 2. Progress simulation normally
step_simulation(state, step_hours=0.25)

# 3. Handle external dynamic event
apply_building_demand_delta(state, delta_kw=25.0)

# 4. State is now fully updated, prioritized, allocated, and ready for frontend polling.
# Serialize for transport:
json_payload = state.model_dump_json()
```

## Example Returned SystemState Structure
The state perfectly serializes into nested JSON:
```json
{
  "simulation": {"simulation_time": 8.25, "simulation_status": "IDLE", ...},
  "environment": {"weather": "SUNNY", "time_of_day": "MORNING"},
  "grid": {"configured_limit_kw": 150.0, "active_limit_kw": 150.0, "current_import_kw": 20.0, ...},
  "building": {"total_demand_kw": 85.0, ...},
  "solar": {"generation_kw": 40.0, ...},
  "stations": [{"station_id": "CS-01", "connected_ev_id": "EV-001", "occupied": true, ...}],
  "evs": [{"ev_id": "EV-001", "current_soc": 20.0, "current_charging_rate_kw": 22.0, "predictive_risk_flag": false, "reason": "Optimal allocation achieved.", ...}],
  "allocations": {"CS-01": 22.0, ...},
  "alerts": [],
  "strategy": "BALANCED",
  "emergency": false
}
```

## Required Integration Assumptions
- **Synchronous Execution**: All functions operate synchronously in-memory. They do not await I/O.
- **Stateless Serialization**: The system relies purely on the Pydantic `SystemState` schema. It contains no circular dependencies, hidden closures, or complex object references. It cleanly serializes via `.model_dump_json()`.
- **Atomic Operations**: State transitions and re-allocations operate as unified atomic sequences via the unified Phase 2/3A/3B pipeline.

## Ownership Boundaries
- **Person 3 Owns**: Simulation clock progression, grid/solar math, predictive risk algorithms, priority weighting logic, explanation generation, and the core deterministic allocation optimizer.
- **Main Backend Owns**: Exposing REST/GraphQL/WebSocket endpoints to frontend clients, handling HTTP sessions and authentication, securely reconstructing/deserializing the `SystemState` from persistence caches or databases, and handling external rate limiting. (No network I/O or WebSockets have been or should be implemented inside the engine).
