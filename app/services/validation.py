from typing import List
from app.models.pydantic_state import SystemState

class ValidationResult:
    def __init__(self, is_valid: bool, errors: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []

class StateValidator:
    """
    Invariant checker. Rejects structurally invalid or dangerous candidate states.
    Does NOT repair, optimize, or fallback state.
    """
    def validate(self, candidate: SystemState) -> ValidationResult:
        errors = []
        
        # Grid bounds
        if candidate.grid.active_limit < 0: errors.append("Grid active_limit cannot be negative")
        if candidate.grid.configured_limit < 0: errors.append("Grid configured_limit cannot be negative")
        if candidate.grid.grid_import < 0: errors.append("Grid import cannot be negative")
        if candidate.grid.available_capacity < 0: errors.append("Grid available_capacity cannot be negative")
        if candidate.grid.grid_import > candidate.grid.active_limit + 1e-4: errors.append("Grid import exceeds active limit")
        
        # Building bounds
        b = candidate.building
        if b.ac_demand < 0 or b.lights_demand < 0 or b.lifts_demand < 0 or b.appliances_demand < 0:
            errors.append("Building component demands cannot be negative")
        if b.total_building_demand < 0:
            errors.append("Building total demand cannot be negative")
        expected_total = b.ac_demand + b.lights_demand + b.lifts_demand + b.appliances_demand + getattr(b, "manual_demand_offset", 0.0)
        if abs(b.total_building_demand - expected_total) > 1e-6:
            errors.append("Building total demand does not match sum of components")
            
        # Solar bounds
        s = candidate.solar
        if s.generation < 0: errors.append("Solar generation cannot be negative")
        if s.usable_solar < 0: errors.append("Usable solar cannot be negative")
        if s.excess_solar < 0: errors.append("Excess solar cannot be negative")
        if s.usable_solar > s.generation: errors.append("Usable solar cannot exceed generation")
        
        # Master Energy Model
        b_demand = b.total_building_demand
        p_total = sum(ev.current_rate for ev in candidate.evs)
        site_load = b_demand + p_total
        
        expected_usable = min(s.generation, site_load)
        expected_excess = max(0.0, s.generation - site_load)
        expected_grid_import = max(0.0, site_load - expected_usable)
        
        if abs(s.usable_solar - expected_usable) > 1e-4:
            errors.append("Usable solar is inconsistent with energy model")
        if abs(s.excess_solar - expected_excess) > 1e-4:
            errors.append("Excess solar is inconsistent with energy model")
        if abs(candidate.grid.grid_import - expected_grid_import) > 1e-4:
            errors.append("Grid import is inconsistent with energy model")
            
        # Emergency Semantics
        if candidate.emergency.emergency_active_state:
            if candidate.grid.active_limit != candidate.emergency.emergency_limit:
                errors.append("Active grid limit must match emergency limit when emergency is active")
        else:
            if candidate.grid.active_limit != candidate.grid.configured_limit:
                errors.append("Active grid limit must match configured limit when emergency is inactive")
                
        # Stations
        station_map = {st.station_id: st for st in candidate.stations}
        for st in candidate.stations:
            if st.capacity < 0: errors.append(f"Station {st.station_id} capacity cannot be negative")
            if st.minimum_charging_rate > st.maximum_charging_rate:
                errors.append(f"Station {st.station_id} min rate exceeds max rate")
            if st.allocated_power < 0: errors.append(f"Station {st.station_id} allocated power cannot be negative")
            if st.allocated_power > st.maximum_charging_rate:
                errors.append(f"Station {st.station_id} allocated power exceeds maximum charging rate")
                
            if st.occupancy and not st.connected_ev_id:
                errors.append(f"Station {st.station_id} is occupied but has no connected EV")
            if not st.occupancy and st.connected_ev_id:
                errors.append(f"Station {st.station_id} is not occupied but has a connected EV")
                
        # EVs
        for ev in candidate.evs:
            if ev.battery_capacity <= 0: errors.append(f"EV {ev.ev_id} battery capacity must be positive")
            if not (0 <= ev.current_soc <= 100): errors.append(f"EV {ev.ev_id} current SOC out of bounds")
            if not (0 <= ev.target_soc <= 100): errors.append(f"EV {ev.ev_id} target SOC out of bounds")
            if ev.current_rate < 0: errors.append(f"EV {ev.ev_id} current rate cannot be negative")
            if ev.current_rate > ev.maximum_rate: errors.append(f"EV {ev.ev_id} current rate exceeds EV max rate")
            if ev.minimum_rate > ev.maximum_rate: errors.append(f"EV {ev.ev_id} min rate exceeds max rate")
            if ev.energy_required < 0: errors.append(f"EV {ev.ev_id} energy required cannot be negative")
            if ev.time_remaining < 0: errors.append(f"EV {ev.ev_id} time remaining cannot be negative")
            if ev.required_average_power < 0: errors.append(f"EV {ev.ev_id} required average power cannot be negative")
            if ev.grid_contribution < 0: errors.append(f"EV {ev.ev_id} grid contribution cannot be negative")
            if ev.solar_contribution < 0: errors.append(f"EV {ev.ev_id} solar contribution cannot be negative")
            
            # Operational state
            current_time = candidate.simulation.simulation_time
            if current_time >= ev.departure and ev.current_rate > 0:
                errors.append(f"EV {ev.ev_id} has departed but still has a charging rate")
            if ev.current_soc >= ev.target_soc and ev.current_rate > 0:
                errors.append(f"EV {ev.ev_id} reached target SOC but still has a charging rate")
                
            if ev.station_id:
                if ev.station_id not in station_map:
                    errors.append(f"EV {ev.ev_id} references nonexistent station {ev.station_id}")
                else:
                    st = station_map[ev.station_id]
                    if st.connected_ev_id != ev.ev_id:
                        errors.append(f"EV {ev.ev_id} assigned to station {st.station_id} but station references {st.connected_ev_id}")
                    if ev.current_rate > st.maximum_charging_rate:
                        errors.append(f"EV {ev.ev_id} current rate exceeds station {st.station_id} max rate")
                        
        # Allocations
        for alloc in candidate.allocations:
            if alloc.allocated_rate < 0: errors.append(f"Allocation for {alloc.ev_id} rate cannot be negative")
            if alloc.grid_contribution < 0: errors.append(f"Allocation for {alloc.ev_id} grid contribution negative")
            if alloc.solar_contribution < 0: errors.append(f"Allocation for {alloc.ev_id} solar contribution negative")
            
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
