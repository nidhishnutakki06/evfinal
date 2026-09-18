# PHASE-03A-REPORT

## Phase
Phase 3A — Priority Engine Only

## Status
PASS

## 1. What was implemented
Implemented the first half of the deterministic engine: a configurable scoring mechanism that standardizes multiple EV urgency indicators into normalized values [0, 1]. This produces an authoritative, reproducible priority order for allocation. Also implemented the instantaneous valid charging bounds and target-safe power calculation.

## 2. Files created / verified
- `src/sh305/engine/priority.py`
- `tests/test_priority.py`
- `docs/implementation-notes/PHASE-03A-REPORT.md`

## 3. Normalized Priority Factors Formulas
Each priority factor yields a value strictly bounded in `[0, 1]`.

1. **SoC Urgency**: 
   `clamp(1.0 - (ev.current_soc / 100.0))`
2. **Deadline Urgency**: 
   `clamp(1.0 - (ev.time_remaining_hours / 12.0))`
3. **Time Pressure**: 
   `clamp(1.0 - (ev.time_remaining_hours / 4.0))`
4. **Energy Need**: 
   `clamp(ev.energy_required_kwh / 100.0)`
5. **Required-Power Pressure**: 
   `clamp(ev.required_average_power_kw / effective_max_kw)`
6. **User Urgency**: 
   Mapping: `LOW=0.25`, `MEDIUM=0.50`, `HIGH=0.75`, `CRITICAL=1.00`.
7. **Feasibility Pressure**: 
   `1.0` if `physical_feasibility` is True AND `current_allocation_feasibility` is False, else `0.0`.
8. **Travel Need**: 
   `clamp(ev.requested_travel_distance_km / ev.expected_range_km)`

## 4. Default Weights
A `WeightConfig` object explicitly manages configuration. Default weights are all `1.0`:
- `w_soc`: 1.0
- `w_deadline`: 1.0
- `w_time`: 1.0
- `w_energy`: 1.0
- `w_required_power`: 1.0
- `w_user`: 1.0
- `w_feasibility`: 1.0
- `w_travel`: 1.0

## 5. Priority Score & Ordering
**Score**: The `priority_score` is the sum of each factor multiplied by its corresponding weight.

**Deterministic Ordering**:
Sorting uses a tuple to guarantee deterministic tie-breaking:
1. `priority_score` DESC
2. `departure_time` ASC
3. `current_soc` ASC
4. `ev_id` ASC

## 6. Charging Constraints
- **control_interval_hours**: A centralized setting defaulting to `0.25` (15 minutes).
- **Target-Safe Power**: `energy_required_kwh / control_interval_hours`. It calculates the exact instantaneous kW limit needed to avoid overshooting the target in a single control interval, intentionally disregarding total remaining time for safety bounds.

## 7. Tests Executed & Results
```bash
python -m pytest tests/test_priority.py -v
```

**Results**:
- 16/16 tests passed.
- Factor bounds strictly enforced (no values < 0 or > 1).
- Time pressure behaves differently than deadline urgency.
- Target-safe power properly prevents overshooting.
- Deterministic ordering correctly applies tie-breakers.

## 8. What Remains for Phase 3B
Phase 3B will finalize the algorithm by introducing:
- The actual constrained deterministic allocator (the algorithm that traverses the prioritized candidates).
- Enforcing global grid/building constraints dynamically across the active EVs.
- The final distribution of power, returning a modified `SystemState` without side-effect mutations.
