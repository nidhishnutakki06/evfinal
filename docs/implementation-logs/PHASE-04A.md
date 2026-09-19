# Phase 4A

Status:
PASS

## Implemented
- 24-hour deterministic simulation engine that advances clock intervals from 00:00 to 24:00.
- Dynamic models for time-of-day mapping, building demand curves, weather impacts, and a synthetic solar generation curve.
- State progression pipeline that processes arrivals, handles departures, and correctly updates EV battery SoC before re-allocating grid resources.

## Files
Created:
- `src/sh305/engine/simulation.py`
- `tests/test_simulation.py`
Modified:
- None

## Core Logic
- simulation design: A centralized `step_simulation` function advances time by `step_hours`, updates environmental and facility variables, processes EV lifecycles, computes the SoC added from the PREVIOUS allocation, and finally fires the Phase 3 `update_state_allocation` pipeline to optimize constraints for the new state.
- step size: Centralized default of `0.25` hours (15 minutes).
- key formulas: 
  - `soc_added = (current_charging_rate_kw * step_hours / battery_capacity_kwh) * 100.0`
  - `solar_curve = max(0.0, 100.0 * sin((time - 6.0) / 12.0 * pi) * weather_factor)`

## Tests
Command:
python -m pytest -v

Result:
Total: 83
Passed: 83
Failed: 0
Skipped: 0

## Numeric Results
- solar drops to exactly 0.0 outside the 6am-6pm window and accurately scales through the day based on `WeatherCondition` multipliers.
- ev arrival/departure successfully binds and frees station assignments (occupancy flags).
- deterministic repeated simulation perfectly replicates the exact final `current_soc` of EVs when run iteratively across deep copied identical states.

## Fixes
- Ensured target SoC capping strictly overrides any further active charging during the SoC update loop before the next allocation begins, avoiding overflow.

## Limitations
- Station assignment logic simply selects the first sequentially un-occupied station; it doesn't currently try to optimally match an EV's max rate with a station's max rate.

## Next Phase
- Phase 4B (Analytics/Reporting, Predictive Features, or Anomalies, based on specification).
