from sh305.integration.adapter import from_backend_state, to_backend_state
from sh305.engine.controller import _recompute, activate_emergency, restore_grid
from sh305.engine.simulation import step_simulation

class EngineBoundary:
    """
    Stateless integration boundary for the Person 3 engine.
    Receives a candidate JSON dictionary, converts it to internal models,
    runs the optimization pipeline, and returns the updated JSON dictionary.
    """
    
    @staticmethod
    def calculate(candidate: dict) -> dict:
        # 1. Convert the backend candidate using the existing compatibility adapter
        state = from_backend_state(candidate)
        
        # Determine if simulation progression is required based on the backend candidate
        sim_dict = candidate.get("simulation", {})
        is_running = sim_dict.get("is_running", False)
        timestep = sim_dict.get("timestep", 0.0)
        
        # 2. Run the existing Person 3 calculation pipeline:
        # If simulation is running and timestep > 0, we advance physics.
        # Note: step_simulation inherently calls _recompute() at the end.
        if is_running and timestep > 0:
            step_simulation(state, step_hours=timestep)
        else:
            # Otherwise, just run the static recompute (A1, A2, A3, A4, requirements, priority, allocation)
            _recompute(state)
            
        # A5 Emergency logic is applied based on the candidate's emergency active state
        # Wait, if we just call activate_emergency(), it will run _recompute() again.
        # But we need to ensure the grid active limit is reduced if emergency is active.
        emg_dict = candidate.get("emergency", {})
        is_emergency = emg_dict.get("emergency_active_state", False)
        emg_limit_fraction = emg_dict.get("emergency_limit", 0.40)
        
        if is_emergency and not state.grid.emergency_mode:
            # Backend requested emergency, but grid hasn't applied the curtailment yet.
            activate_emergency(state, reduction_fraction=emg_limit_fraction)
        elif not is_emergency and state.grid.emergency_mode:
            # Backend requested restore, but grid is still curtailed.
            restore_grid(state)
        elif is_emergency and state.grid.emergency_mode:
             # Emergency already active, make sure grid limit reflects the requested fraction just in case
             # Activate emergency idempotently applies the limit and recomputes
             activate_emergency(state, reduction_fraction=emg_limit_fraction)
            
        # 4. Convert the result back to the frozen backend SystemState
        updated_candidate = to_backend_state(state)
        
        # 5. Return the updated candidate/result
        return updated_candidate
