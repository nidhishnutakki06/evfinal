from sh305.domain.system_state import SystemState
from sh305.engine import requirements, energy, feasibility, priority
from sh305.engine.optimizer import allocate_charging
from sh305.engine.priority import WeightConfig, identify_candidates
from sh305.engine.explanations import generate_explanations
from sh305.engine.prediction import calculate_predictive_risk

def update_state_requirements_and_energy(state: SystemState, reserve_percent: float = 10.0) -> None:
    """
    Main Phase 2 orchestration function.
    Calculates and updates requirements, projections, and energy variables.
    Does NOT calculate priority or enforce allocations.
    """
    simulation_time = state.simulation.simulation_time
    
    # 1. Update EVs
    for ev in state.evs:
        # Target SoC & Energy
        ev.target_soc = requirements.calculate_target_soc(ev, reserve_percent)
        ev.energy_required_kwh = requirements.calculate_energy_required(ev)
        
        # Time & Power Requirements
        ev.time_remaining_hours = requirements.calculate_time_remaining(ev, simulation_time)
        ev.required_average_power_kw = requirements.calculate_required_power(ev)
        
        # Completion Estimates
        ev.estimated_completion_time = requirements.estimate_completion_time(ev, simulation_time)
        ev.estimated_soc_at_departure = requirements.estimate_soc_at_departure(ev)
        
        # Feasibility
        station = next((s for s in state.stations if s.station_id == ev.station_id), None)
        effective_max = feasibility.calculate_effective_max(ev, station)
        ev.physical_feasibility = feasibility.calculate_physical_feasibility(ev, effective_max)
        ev.current_allocation_feasibility = feasibility.calculate_current_allocation_feasibility(ev)
        
    # 2. Update Site Energy
    site_load = energy.calculate_site_load(state.building, state.evs)
    usable_solar = energy.calculate_usable_solar(state.solar, site_load)
    
    state.solar.usable_solar_kw = usable_solar
    state.solar.excess_solar_kw = energy.calculate_excess_solar(state.solar, site_load)
    
    grid_import = energy.calculate_grid_import(site_load, usable_solar)
    state.grid.current_import_kw = grid_import
    state.grid.available_capacity_kw = energy.calculate_available_grid_capacity(state.grid, grid_import)

def update_state_allocation(state: SystemState, weights: WeightConfig, control_interval_hours: float = 0.25, reserve_percent: float = 10.0) -> None:
    """
    Phase 3B main orchestration function.
    Runs Phase 2, calculates priorities, allocates power, and updates the state.
    """
    # 1. run Phase 2 calculations
    update_state_requirements_and_energy(state, reserve_percent)
    
    # 2. run Phase 3A priority calculation
    candidates = identify_candidates(state, weights, control_interval_hours)
    
    # 3. run optimizer
    results = allocate_charging(state, candidates, control_interval_hours)
    
    # 4. validate allocation & 5. update EV charging rates
    for result in results:
        ev = next(ev for ev in state.evs if ev.ev_id == result.ev_id)
        ev.current_charging_rate_kw = result.allocated_power_kw
        # We remove the naive reason generator from here, because Phase 5A generates detailed deterministic reasons.
        # ev.reason is now assigned by generate_explanations() below
            
    # 6. update station allocated power
    for station in state.stations:
        station_evs = [ev for ev in state.evs if ev.station_id == station.station_id]
        station.current_allocated_power_kw = sum(ev.current_charging_rate_kw for ev in station_evs)
        
    # 7. rerun Phase 2 site-energy calculations
    site_load = energy.calculate_site_load(state.building, state.evs)
    usable_solar = energy.calculate_usable_solar(state.solar, site_load)
    
    state.solar.usable_solar_kw = usable_solar
    state.solar.excess_solar_kw = energy.calculate_excess_solar(state.solar, site_load)
    
    grid_import = energy.calculate_grid_import(site_load, usable_solar)
    state.grid.current_import_kw = grid_import
    state.grid.available_capacity_kw = energy.calculate_available_grid_capacity(state.grid, grid_import)
    
    # 8. Phase 5A: A2 Generate Explanations and A3 Calculate Predictive Risk
    generate_explanations(state, control_interval_hours)
    calculate_predictive_risk(state)
