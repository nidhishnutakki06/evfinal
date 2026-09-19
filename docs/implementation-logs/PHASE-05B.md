# Phase 5B

Status:
PASS

## Implemented
- A4 Strategy Switcher allowing dynamic reconfiguration of priorities via exactly three distinct operating modes: `DEADLINE_FIRST`, `SOLAR_FIRST`, and `GRID_SAFETY_FIRST`. (`BALANCED` was removed as a selectable strategy).
- Centralized strategy-to-weight mappings directly integrated into the single existing deterministic allocator.
- Extended the PriorityFactors model and `calculate_priority_score` with `solar_alignment` and `grid_safety` calculations based on live state.
- Strictly maintained A4 as objective weighting only. All strategies utilize the identical optimizer and are bounded by identical hard constraints, notably ensuring that allocations never bypass `target_safe_power` caps.

## Files
Created:
- `tests/test_strategies.py`
Modified:
- `src/sh305/engine/priority.py`
- `src/sh305/engine/controller.py`
- `src/sh305/engine/optimizer.py`

## Core Logic
- `set_strategy(state, strategy)` updates the active string identifier, loads corresponding `WeightConfig`, and executes a full `_recompute()`.
- Strategy configurations shift priority focus by augmenting specific weights (e.g., `w_deadline`, `w_time`, `w_solar_alignment`).
- Hard constraints (site grid limit, station limits, physical battery limits, and target safe power smoothing constraints) are securely maintained within the single optimization funnel across all strategies.

## Tests
Command:
python -m pytest -v

Result:
Total: 109
Passed: 109
Failed: 0
Skipped: 0

## Numeric Results
- **Correction Applied**: Ensured Solar-first uses the same target-safe-power cap as all other strategies, without any bypass logic.
- **Strategy Set Tested**: `DEADLINE_FIRST`, `SOLAR_FIRST`, `GRID_SAFETY_FIRST`.
- **Strategy-dependent allocation difference demonstrated**: Yes, a genuine difference was verified. We validated that the `SOLAR_FIRST` difference is genuinely caused by the renewable-utilization objective, which mathematically derives a score based on how much of the current solar generation the EV's required power can absorb (`ev.required_average_power_kw / state.solar.generation_kw`). We updated the test to tie the preference directly to the varying energy requirements of EVs, confirming that the priority shift is explicitly driven by solar utilization capability rather than merely having a larger maximum charging capacity.
- **Constraints Maintained**: Both strategies correctly adhered to grid limits without violating physical limits or exceeding the target_safe_power maximum limit.

## Fixes
- Removed `BALANCED` from the available strategy list and forced usage of strictly defined A4 strategies.
- Removed the previously implemented Solar-first optimizer target-safe bypass. A4 objective priority shifts must occur natively through sorting, not logic bypasses.
- Prevented dynamic `current_allocation_feasibility` feedback loop cross-contamination during testing by copying state snapshots.

## Limitations
- Solar-first differences manifest strictly via sorting candidate priority. If multiple EVs are fully bottlenecked by identical `target_safe_power` limits rather than by max capacity limitations, differences in absolute kW allocations between strategies may be negligible.

## Next Phase
- Phase 6 (if any) or project conclusion.
