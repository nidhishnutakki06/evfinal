from pydantic import BaseModel
from app.models.pydantic_state import SystemState

class CalculationContext(BaseModel):
    """
    Input context provided to the engine boundary.
    Conceptually holds all necessary state to perform optimizations.
    """
    state: SystemState

class CalculationResult(BaseModel):
    """
    Result returned by the simulation/optimization engine.
    For Phase 7, this is a deterministic, empty placeholder to prove the pipeline works
    without implementing premature logic.
    """
    pass

class EngineBoundary:
    """
    Interface for the simulation/optimization engine.
    Calculates EV priorities, allocations, and grid math based on the provided context.
    Returns deterministic results to be assembled into the canonical state by the backend.
    """
    def calculate(self, context: CalculationContext) -> CalculationResult:
        # Development/Test mock implementation.
        # We calculate the fundamental energy physics (SITE_LOAD, USABLE_SOLAR, GRID_IMPORT)
        # to ensure the state passes strict structural validation in Phase 9, 
        # without implementing any EV allocation optimization.
        state = context.state
        
        b_demand = state.building.total_building_demand
        p_total = sum(ev.current_rate for ev in state.evs)
        site_load = b_demand + p_total
        
        s = state.solar.generation
        usable_solar = min(s, site_load)
        excess_solar = max(0.0, s - site_load)
        grid_import = max(0.0, site_load - usable_solar)
        
        state.solar.usable_solar = usable_solar
        state.solar.excess_solar = excess_solar
        state.grid.grid_import = grid_import
        
        return CalculationResult()
