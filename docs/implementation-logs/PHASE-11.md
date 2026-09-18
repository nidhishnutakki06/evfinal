# Phase 11: Simulation/Optimization Integration

Status: PASS

## Goal
Connect the existing Person 3 engine to the backend's frozen integration boundary (`app.core.engine_boundary.EngineBoundary.calculate()`).

## Important Architecture Rules Followed
- Did NOT create a persistent/class-level shadow `SystemState` inside `EngineBoundary`.
- The backend `candidate` dictionary acts as the single authoritative canonical state.
- Used the exact backend contract names as instructed (`simulation.simulation_time`, `simulation.is_running`, `emergency.emergency_active_state`, `building.ac_demand`, etc.).
- `total_building_demand` is treated as a derived state.
- Implemented the flow: `REST candidate -> adapter -> EngineSystemState -> Engine recalculation/physics -> adapter -> backend candidate`.

## Files Changed
- `src/sh305/integration/adapter.py`: Refactored to completely instantiate a new `SystemState` from the provided candidate dictionary, adhering strictly to the backend schema names requested.
- `src/app/core/engine_boundary.py`: Created the stateless boundary class mapping the candidate JSON directly into the engine's internal models, conditionally invoking physics (A4, A5, simulation), running `_recompute()`, and serializing back.
- `src/app/__init__.py` and `src/app/core/__init__.py`: Created for Python package resolution.
- `tests/test_backend_compatibility.py`: Updated to match the new `adapter.py` signature.
- `tests/test_engine_boundary.py`: Added 5 focused tests proving A1-A5 integration without breaking determinism or state validation.

## EngineBoundary Behavior
- Checks if the backend requested a simulation timestep (`is_running` and `timestep > 0`) and triggers `step_simulation()`.
- Synchronizes grid curtailment limits based on `emergency.emergency_active_state` (A5).
- Relies on `from_backend_state` to sync dynamic building/grid/strategy requests (A1, A4).
- Always triggers the `_recompute()` pipeline to run the deterministic optimizer and preserve mathematical limits, battery bounds, priority scoring, explanations (A2), and risk predictions (A3).
- Outputs the canonical `SystemState` preserving frozen schema compatibility.

## Assumptions / Discrepancies
- The README explicitly mentions `SITE_LOAD` as a derived value, but it is not modeled as a top-level field in the frozen schema. We respected this frozen schema condition and did not invent it in the returned dictionary.
- We assumed new EV arrivals are already instantiated in the `candidate` payload array by the upstream `REST` caller, so the adapter parses and links them transparently.

## Tests & Results
- Regression suite passing: 127/127 (including 5 new `EngineBoundary` integration tests).
- All domain rules and previous test constraints remain untouched.
