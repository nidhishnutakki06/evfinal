from typing import Optional
from sh305.domain.ev import EV

def calculate_target_soc(ev: EV, reserve_percent: float = 10.0) -> float:
    """
    Calculates target SoC based on requested travel distance and expected range.
    trip_soc = (requested_travel_distance_km / expected_range_km) * 100
    target_soc = current_soc OR (trip_soc + reserve_percent), capped at 100.
    """
    if ev.expected_range_km <= 0:
        return ev.current_soc
    
    trip_soc = (ev.requested_travel_distance_km / ev.expected_range_km) * 100.0
    desired_soc = trip_soc + reserve_percent
    
    target_soc = max(ev.current_soc, desired_soc)
    return min(100.0, target_soc)

def calculate_energy_required(ev: EV) -> float:
    """
    Calculates the required energy in kWh to reach the target SoC.
    Returns 0 if already reached or exceeded.
    """
    if ev.target_soc is None:
        return 0.0
        
    if ev.current_soc >= ev.target_soc:
        return 0.0
        
    return ((ev.target_soc - ev.current_soc) / 100.0) * ev.battery_capacity_kwh

def calculate_time_remaining(ev: EV, simulation_time: float) -> float:
    """
    Calculates time remaining until departure in hours.
    Can return zero or negative values.
    """
    return ev.departure_time - simulation_time

def calculate_required_power(ev: EV) -> float:
    """
    Calculates required average power in kW to reach the target SoC.
    Returns 0 if no energy is required or time remaining is <= 0.
    """
    if ev.energy_required_kwh <= 0:
        return 0.0
        
    if ev.time_remaining_hours <= 0:
        return 0.0
        
    return ev.energy_required_kwh / ev.time_remaining_hours

def estimate_completion_time(ev: EV, simulation_time: float) -> Optional[float]:
    """
    Estimates the completion simulation time based on the current charging rate.
    If energy is 0, returns simulation time.
    If charging rate is 0, returns None.
    """
    if ev.energy_required_kwh <= 0:
        return simulation_time
        
    if ev.current_charging_rate_kw <= 0:
        return None
        
    charging_duration = ev.energy_required_kwh / ev.current_charging_rate_kw
    return simulation_time + charging_duration

def estimate_soc_at_departure(ev: EV) -> float:
    """
    Estimates the SoC at departure time if the current charging rate continues.
    Projected energy is clamped so it does not exceed 100%.
    Time remaining <= 0 produces current_soc.
    """
    if ev.time_remaining_hours <= 0:
        return ev.current_soc
        
    energy_added = ev.current_charging_rate_kw * ev.time_remaining_hours
    projected_soc = ev.current_soc + (energy_added / ev.battery_capacity_kwh * 100.0)
    
    return min(100.0, max(0.0, projected_soc))
