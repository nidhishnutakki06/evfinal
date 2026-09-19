# PHASE-02-REPORT

## Phase
Phase 2 — Energy Model + EV Requirements + Feasibility

## Status
PASS

## 1. What was implemented
Implemented the deterministic mathematical layer that derives EV charging requirements, state projections, charging feasibility flags, and authoritative site energy load constraints based on the foundational models from Phase 1. An orchestrating updater function was built to derive all values in a pure and repeatable manner.

## 2. Files created
- `src/sh305/engine/__init__.py`
- `src/sh305/engine/requirements.py`
- `src/sh305/engine/energy.py`
- `src/sh305/engine/feasibility.py`
- `src/sh305/engine/updater.py`
- `tests/test_requirements.py`
- `tests/test_energy.py`
- `tests/test_feasibility.py`
- `docs/implementation-notes/PHASE-02-REPORT.md`

## 3. Files modified
None (all logic was modularly added on top of Phase 1 foundation using new engine classes/functions).

## 4. Target SoC formula
The `target_soc` represents the travel-need-based charge state. The formula is:
```text
trip_soc = (requested_travel_distance_km / expected_range_km) * 100
desired_soc = trip_soc + reserve_percent
target_soc = min(100, max(current_soc, desired_soc))
```
The `reserve_percent` defaults to `10.0` but is fully configurable in the updater orchestrator function. Target SoC is strictly bounded above the `current_soc` and capped at a maximum of `100.0`.

## 5. Energy requirement
The `energy_required_kwh` calculates the kWh required to hit the target:
```text
if current_soc >= target_soc: 
    energy_required_kwh = 0
else:
    energy_required_kwh = ((target_soc - current_soc) / 100) * battery_capacity_kwh
```

## 6. Time / required power
**Time remaining**:
```text
time_remaining_hours = departure_time - simulation_time
```
This is allowed to be negative or zero without crashing. 

**Required average power**:
```text
if energy_required_kwh > 0 and time_remaining_hours > 0:
    required_average_power_kw = energy_required_kwh / time_remaining_hours
else:
    required_average_power_kw = 0
```

## 7. Feasibility
Two entirely distinct feasibility flags are provided:
- **Physical Feasibility**: Answers "Can this EV physically reach its target by departure if it receives the maximum physically feasible charging rate?".
  - `effective_max = min(ev.max_rate, station.max_rate)` (0 if no station).
  - `max_deliverable_energy = effective_max * time_remaining_hours`
  - `physical_feasibility = max_deliverable_energy >= energy_required_kwh`
- **Current-Allocation Feasibility**: Answers "Can this EV reach its target if its CURRENT charging rate continues until departure?".
  - `projected_energy = current_charging_rate_kw * time_remaining_hours`
  - `current_allocation_feasibility = projected_energy >= energy_required_kwh`

The two concepts were explicitly proven to be independent through testing.

## 8. Projection logic
These fields assume the `current_charging_rate_kw` is held steady. They do NOT dictate allocation.
- **Estimated Completion Time**: `simulation_time + (energy_required_kwh / current_charging_rate_kw)`. If no energy is needed, returns `simulation_time`. If rate is 0, returns `None`.
- **Estimated SoC at Departure**: `current_soc + ( (current_rate * time_remaining) / battery_capacity * 100 )`. Bounded strictly within `[0, 100]`.

## 9. Site energy model
Authoritative electrical state calculations:
```text
SITE_LOAD = building.total_demand_kw + P_total
USABLE_SOLAR = min(solar.generation_kw, SITE_LOAD)
EXCESS_SOLAR = max(0, solar.generation_kw - SITE_LOAD)
GRID_IMPORT = max(0, SITE_LOAD - USABLE_SOLAR)
AVAILABLE_GRID_CAPACITY = max(0, grid.active_limit_kw - GRID_IMPORT)
```

## 10. EV demand source
Phase 2 exclusively uses `EV.current_charging_rate_kw` as the singular authoritative current EV charging demand input for the calculation of `P_total`.

## 11. Tests executed
```bash
python -m pytest -v
```

## 12. Test results
```text
Total: 47
Passed: 47
Failed: 0
Skipped: 0
```

## 13. Numeric verification
**Case A (Target SoC & Energy)**: 
Battery=60, SoC=20, Target=50 -> Expected & Calculated: `18.0 kWh`
**Case B (Required Power)**: 
Required=18, Time=3 -> Expected & Calculated: `6.0 kW`
**Case C (Effective Max)**: 
EV max=11, Station max=7.4 -> Expected & Calculated: `7.4 kW`
**Case D (Independence)**: 
Required=24, Time=3 (Avg 8), Max=11, Alloc=4 -> Physical: `True`, Allocation: `False`.
**Case E (Energy Model Overload)**: 
Bldg=91, EV=0, Solar=35 -> Site Load: 91, Usable Solar: 35, Excess Solar: 0, Grid Import: 56
**Case F (Solar > Load)**: 
Bldg=10, EV=0, Solar=50 -> Grid Import: 0, Excess Solar: 40

## 14. Phase boundary
What was explicitly NOT implemented:
- Adjusting or allocating EV charging rates to repair constraints.
- Priority scoring algorithms.
- Any predictive risk triggers or 24-hour simulation loops.

## 15. Design decisions
- The Phase 2 orchestrator function `update_state_requirements_and_energy` iterates over the objects within the passed `SystemState` applying functions from the dedicated pure submodules (`energy`, `requirements`, `feasibility`), rather than implementing math methods directly onto the Pydantic models. This avoids polluting domain models with behavioral methods while keeping execution easily testable.

## 16. Known limitations
- The equations produce instantaneous snapshots; without a simulation clock delta, projections depend on static mathematical extrapolations without accounting for potential charging curves (which may be a feature, depending on downstream phase logic).

## 17. Next phase
Phase 3 will introduce:
- Normalized priority factors.
- Objective weighting.
- Deterministic constrained optimizer.
- Actual EV charging allocation algorithm.
- Enforcement of grid constraints against allocations.
