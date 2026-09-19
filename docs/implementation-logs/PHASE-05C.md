# Phase 5C

Status: PASS

## Files
- `src/sh305/engine/controller.py` (Modified)
- `tests/test_emergency.py` (Created)

## Emergency Behavior
- `activate_emergency(state)` applies a percentage reduction to the configured grid limit, setting it as the new active limit.
- Immediately calls the standard `_recompute()` pipeline.
- The existing optimizer natively enforces the new stricter grid limit. Lower-priority EVs that can no longer receive their minimum charging rate are cleanly paused without violating constraints or issuing sub-minimum allocations.
- A2 (Explanations) and A3 (Predictive Risk) are triggered immediately via the standard pipeline.

## Recovery Behavior
- `restore_grid(state)` resets the active limit back to the original configured limit.
- Re-runs `_recompute()`.
- The optimizer natively re-allocates available capacity based on the current priorities, smoothly resuming EVs without blindly restoring stale past rates.

## Tests & Results
- Total tests: 115
- Passed: 115
- `test_emergency.py` covers emergency activation, safe reduction, zero-sub-minimum enforcement, explanation/risk updates, correct recovery allocation, and deterministic behavior.

## Key Numeric Example
- **Initial**: Grid limit 50.0 kW, Building load 10.0 kW. Available EV capacity: 40.0 kW. EV1 (Critical) receives 22.0 kW, EV2 (Low) receives 7.0 kW.
- **Emergency**: 60% reduction. New limit 20.0 kW. Available EV capacity: 10.0 kW. EV1 gets 10.0 kW (still ≥ min 7.0 kW). EV2 paused (0.0 kW) since remaining 0.0 kW < its min 7.0 kW.

## Limitations
- Grid limits apply globally. Does not support independent station-level islanding.
