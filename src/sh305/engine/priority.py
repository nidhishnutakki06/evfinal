from typing import List
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from sh305.domain.ev import EV
from sh305.domain.station import Station
from sh305.domain.system_state import SystemState
from sh305.domain.enums import UserUrgency
from sh305.engine import feasibility

class WeightConfig(BaseModel):
    w_soc: float = 1.0
    w_deadline: float = 1.0
    w_time: float = 1.0
    w_energy: float = 1.0
    w_required_power: float = 1.0
    w_user: float = 1.0
    w_feasibility: float = 1.0
    w_travel: float = 1.0
    w_solar_alignment: float = 0.0
    w_grid_safety: float = 0.0

STRATEGY_WEIGHTS = {
    "DEADLINE_FIRST": WeightConfig(
        w_deadline=2.0, w_time=2.0, w_required_power=1.5, w_feasibility=2.0
    ),
    "SOLAR_FIRST": WeightConfig(
        w_solar_alignment=2.0, w_energy=1.5
    ),
    "GRID_SAFETY_FIRST": WeightConfig(
        w_grid_safety=2.0, w_required_power=0.5
    )
}

class PriorityFactors(BaseModel):
    soc_urgency: float
    deadline_urgency: float
    time_urgency: float
    energy_need: float
    required_power_pressure: float
    user_urgency: float
    feasibility_pressure: float
    travel_need: float
    solar_alignment: float
    grid_safety: float

def _clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    return max(min_val, min(max_val, value))

def calc_soc_urgency(ev: EV) -> float:
    return _clamp(1.0 - (ev.current_soc / 100.0))

def calc_deadline_urgency(ev: EV, normalization_hours: float = 12.0) -> float:
    return _clamp(1.0 - (ev.time_remaining_hours / normalization_hours))

def calc_time_urgency(ev: EV, time_normalization_hours: float = 4.0) -> float:
    # Distinct from deadline: emphasizes shrinking charging window.
    return _clamp(1.0 - (ev.time_remaining_hours / time_normalization_hours))

def calc_energy_need(ev: EV, normalization_kwh: float = 100.0) -> float:
    return _clamp(ev.energy_required_kwh / normalization_kwh)

def calc_required_power_pressure(ev: EV, effective_max_kw: float) -> float:
    if effective_max_kw <= 0:
        return 0.0
    return _clamp(ev.required_average_power_kw / effective_max_kw)

def calc_user_urgency(ev: EV) -> float:
    mapping = {
        UserUrgency.LOW: 0.25,
        UserUrgency.MEDIUM: 0.50,
        UserUrgency.HIGH: 0.75,
        UserUrgency.CRITICAL: 1.00
    }
    return mapping.get(ev.user_urgency, 0.50)

def calc_feasibility_pressure(ev: EV) -> float:
    if ev.physical_feasibility is True and ev.current_allocation_feasibility is False:
        return 1.0
    return 0.0

def calc_travel_need(ev: EV) -> float:
    if ev.expected_range_km <= 0:
        return 0.0
    return _clamp(ev.requested_travel_distance_km / ev.expected_range_km)

def calc_solar_alignment(ev: EV, state: SystemState = None) -> float:
    """
    Mathematically derives alignment: how much of the CURRENT solar generation 
    can this EV's required power absorb?
    """
    if not state or state.solar.generation_kw <= 0:
        return 0.0
    return _clamp(ev.required_average_power_kw / state.solar.generation_kw)

def calc_grid_safety(ev: EV, state: SystemState = None) -> float:
    """
    Mathematically derives safety: inversely proportional to the EV's 
    power demand relative to the CURRENT active grid limit.
    """
    grid_limit = state.grid.active_limit_kw if state else 50.0
    if grid_limit <= 0:
        return 0.0
    return _clamp(1.0 - (ev.required_average_power_kw / grid_limit))

def calculate_priority_factors(ev: EV, effective_max_kw: float, state: SystemState = None) -> PriorityFactors:
    # Handle optional state for tests that might not pass it directly
    solar_align = calc_solar_alignment(ev, state)
    grid_safe = calc_grid_safety(ev, state)
    return PriorityFactors(
        soc_urgency=calc_soc_urgency(ev),
        deadline_urgency=calc_deadline_urgency(ev),
        time_urgency=calc_time_urgency(ev),
        energy_need=calc_energy_need(ev),
        required_power_pressure=calc_required_power_pressure(ev, effective_max_kw),
        user_urgency=calc_user_urgency(ev),
        feasibility_pressure=calc_feasibility_pressure(ev),
        travel_need=calc_travel_need(ev),
        solar_alignment=solar_align,
        grid_safety=grid_safe
    )

def calculate_priority_score_from_factors(factors: PriorityFactors, weights: WeightConfig) -> float:
    return (
        weights.w_soc * factors.soc_urgency +
        weights.w_deadline * factors.deadline_urgency +
        weights.w_time * factors.time_urgency +
        weights.w_energy * factors.energy_need +
        weights.w_required_power * factors.required_power_pressure +
        weights.w_user * factors.user_urgency +
        weights.w_feasibility * factors.feasibility_pressure +
        weights.w_travel * factors.travel_need +
        weights.w_solar_alignment * factors.solar_alignment +
        weights.w_grid_safety * factors.grid_safety
    )

def calculate_priority_score(ev: EV, effective_max_kw: float, weights: WeightConfig, state: SystemState = None) -> float:
    factors = calculate_priority_factors(ev, effective_max_kw, state)
    return calculate_priority_score_from_factors(factors, weights)

# Common priority ordering definition
def sort_candidates(candidates: List['Candidate']) -> List['Candidate']:
    return sorted(candidates, key=lambda c: (
        -c.priority_score,
        c.ev.departure_time,
        c.ev.current_soc,
        c.ev.ev_id
    ))

class Candidate(BaseModel):
    ev: EV
    station: Station
    effective_max_kw: float
    valid_min_kw: float
    target_safe_power_kw: float
    p_max: float
    factors: PriorityFactors
    priority_score: float

def identify_candidates(state: SystemState, weights: WeightConfig, control_interval_hours: float = 0.25) -> List[Candidate]:
    candidates = []
    
    for ev in state.evs:
        # Must be connected and assigned to a station
        if not ev.station_id:
            continue
            
        station = next((s for s in state.stations if s.station_id == ev.station_id), None)
        if not station:
            continue
            
        # Not departed
        if ev.time_remaining_hours <= 0:
            continue
            
        # Not already at target (no energy required)
        if ev.energy_required_kwh <= 0:
            continue
            
        # Effective max and valid min
        effective_max_kw = min(ev.max_charging_rate_kw, station.max_charging_rate_kw)
        valid_min_kw = max(ev.min_charging_rate_kw, station.min_charging_rate_kw)
        
        # Capable of receiving a valid rate
        if valid_min_kw > effective_max_kw:
            continue
            
        target_safe_power = ev.energy_required_kwh / control_interval_hours
        p_max = min(effective_max_kw, target_safe_power)
        
        if valid_min_kw > p_max or effective_max_kw <= 0:
            continue
            
        factors = calculate_priority_factors(ev, effective_max_kw, state)
        score = calculate_priority_score_from_factors(factors, weights)
        
        candidates.append(Candidate(
            ev=ev,
            station=station,
            effective_max_kw=effective_max_kw,
            valid_min_kw=valid_min_kw,
            target_safe_power_kw=target_safe_power,
            p_max=p_max,
            factors=factors,
            priority_score=score
        ))
        
    return sort_candidates(candidates)
