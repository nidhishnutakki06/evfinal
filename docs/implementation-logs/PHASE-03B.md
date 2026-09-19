# Phase 3B

Status:
PASS

## Implemented
- Deterministic charging allocator (`optimizer.py`) combining Phase 2 capacity limits and Phase 3A priorities.
- Single common allocator enforcing EV minimums, station max limits, target safe bounds, and dynamic grid caps.
- Synchronized state updating function (`update_state_allocation`) ensuring unified calculation sequences.

## Files
Created:
- `src/sh305/engine/optimizer.py`
- `tests/test_optimizer.py`
Modified:
- `src/sh305/engine/updater.py`

## Core Logic
- allocator method: Iterates linearly over priority-sorted candidates. Determines instantaneous grid capacity constraint, bounds against EV and Station max/min limits, and allocates charging power.
- important constraints: Never assigns sub-minimum charging. Puts safe limits against `p_max = min(effective_max, target_safe_power, station_capacity)`. Ensures `GRID_IMPORT <= grid.active_limit_kw`.
- important formulas: `available_ev_capacity = max(0.0, grid.active_limit_kw - building.total_demand_kw + solar.generation_kw)`

## Tests
Command:
python -m pytest -v

Result:
Total: 75
Passed: 75
Failed: 0
Skipped: 0

## Numeric Results
- normal capacity: Two identical EVs without a constraint both received 11.0 kW charging rate.
- grid-constrained case: Remaining 15.0 kW split strictly based on urgency priorities (CRITICAL EV took 11.0 kW, LOW EV took remaining 4.0 kW).
- minimum-rate conflict: EV allocated 4.0 kW was paused because its `valid_min` was 5.0 kW, protecting lower bounds.
- solar headroom: Building = 20, Solar = 50, Grid limit = 100 correctly produced an available EV capacity of 130 kW, fully utilizing the raw solar headroom.
- solar exceeds site load: When site load (21 kW) was less than solar generation (50 kW), the `GRID_IMPORT` was safely evaluated to 0.0 kW and `EXCESS_SOLAR` to 29.0 kW correctly.

## Fixes
- Corrected the initial aggregate EV capacity bound `available_ev_capacity` to use raw `solar.generation_kw` instead of `usable_solar_kw`, preventing artificial capacity truncation.

## Limitations
- Operates entirely on the static snapshot of the system state. Does not project or react dynamically to moving weather parameters ahead of schedule (which will come in Phase 4 loops).

## Next Phase
- Phase 4 will implement the 24-hour simulation loop to continually advance clock intervals and repeatedly trigger this state synchronization algorithm.
