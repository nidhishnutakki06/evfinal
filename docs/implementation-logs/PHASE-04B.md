# Phase 4B

Status:
PASS

## Implemented
- Central dynamic event controller handling A1 manual overrides (building demand delta, grid limit delta, weather condition override, and synthetic EV spawning).

## Files
Created:
- `src/sh305/engine/controller.py`
- `tests/test_controller.py`
Modified:
- None

## Core Logic
- A1 controls: `apply_building_demand_delta`, `apply_grid_limit_delta`, `change_weather`, `spawn_ev`, `spawn_urgent_ev`.
- recomputation flow: Every control executes an immediate, direct modification to the canonical `SystemState` followed instantly by a central `_recompute()` pipeline. This ensures the full Phase 2 (requirements) + Phase 3A (priority) + Phase 3B (allocator) pipeline is strictly observed, retaining a single authoritative state pathway.

## Tests
Command:
python -m pytest -v

Result:
Total: 91
Passed: 91
Failed: 0
Skipped: 0

## Numeric Results
- grid safety: Safely handles huge building demand deltas (e.g., adding 160 kW) by immediately triggering capacity restrictions that force the EV allocator to gracefully pause (`0.0 kW`) or dynamically minimize rates under constraints.
- weather immediate response: Altering weather condition to `RAIN` correctly throttled immediate solar generation and propagated limits to the allocator in the same execution tick.
- unavailable stations: The controller securely intercepts and rejects EV spawning (raising `RuntimeError`) when station occupancy is totally full.

## Limitations
- State modifications are completely un-debounced at the domain level; the external frontend service must orchestrate slider debouncing before dispatching calls.

## Next Phase
- Phase 5 (Remaining A2–A5 controls, UI/Frontend bindings, and final reporting mechanisms).
