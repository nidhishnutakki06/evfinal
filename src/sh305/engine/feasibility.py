from typing import Optional
from sh305.domain.ev import EV
from sh305.domain.station import Station

def calculate_effective_max(ev: EV, station: Optional[Station]) -> float:
    """
    Calculates the maximum physically feasible charging rate considering the EV and the Station.
    Returns 0 if no station is connected.
    """
    if station is None:
        return 0.0
        
    return min(ev.max_charging_rate_kw, station.max_charging_rate_kw)

def calculate_physical_feasibility(ev: EV, effective_max_kw: float) -> bool:
    """
    Evaluates if the EV can reach its target energy receiving the max feasible rate.
    """
    if ev.energy_required_kwh <= 0:
        return True
        
    if effective_max_kw <= 0:
        return False
        
    if ev.time_remaining_hours <= 0:
        return False
        
    max_deliverable = effective_max_kw * ev.time_remaining_hours
    return max_deliverable >= ev.energy_required_kwh

def calculate_current_allocation_feasibility(ev: EV) -> bool:
    """
    Evaluates if the EV can reach its target energy using its current charging rate.
    """
    if ev.energy_required_kwh <= 0:
        return True
        
    if ev.time_remaining_hours <= 0:
        return False
        
    projected_energy = ev.current_charging_rate_kw * ev.time_remaining_hours
    return projected_energy >= ev.energy_required_kwh
