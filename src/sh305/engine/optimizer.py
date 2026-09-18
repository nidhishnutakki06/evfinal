from typing import List
from pydantic import BaseModel
from sh305.domain.system_state import SystemState
from sh305.engine.priority import Candidate

class AllocationResult(BaseModel):
    ev_id: str
    allocated_power_kw: float
    status: str
    effective_max_kw: float
    valid_min_kw: float
    priority_score: float

def allocate_charging(state: SystemState, candidates: List[Candidate], control_interval_hours: float = 0.25) -> List[AllocationResult]:
    # 1. Determine total power available for EVs from the grid perspective
    # Grid Import = max(0, Building + P_total - Solar)
    # We need Grid Import <= Grid Active Limit
    # Building + P_total - Solar <= Grid Active Limit
    # P_total <= Grid Active Limit + Solar - Building
    available_ev_capacity = max(0.0, state.grid.active_limit_kw - state.building.total_demand_kw + state.solar.generation_kw)
    
    results = []
    allocated_ev_ids = set()
    
    for candidate in candidates:
        ev = candidate.ev
        station = candidate.station
        allocated_ev_ids.add(ev.ev_id)
        
        # p_max and valid_min are pre-calculated in Candidate
        # However, we must also ensure we respect station_capacity_kw if it's smaller
        effective_max = candidate.effective_max_kw
        p_max = min(candidate.p_max, station.station_capacity_kw)
        valid_min = candidate.valid_min_kw
        
        # Check if we can allocate valid_min based on grid capacity
        # Grid safety constraint
        max_allocatable = min(p_max, available_ev_capacity)
        
        if valid_min > p_max or max_allocatable < valid_min:
            # Conflict or insufficient power -> Pause
            results.append(AllocationResult(
                ev_id=ev.ev_id,
                allocated_power_kw=0.0,
                status="PAUSED",
                effective_max_kw=effective_max,
                valid_min_kw=valid_min,
                priority_score=candidate.priority_score
            ))
        else:
            # Allocate available power up to p_max
            allocated = max_allocatable
            available_ev_capacity -= allocated
            
            results.append(AllocationResult(
                ev_id=ev.ev_id,
                allocated_power_kw=allocated,
                status="CHARGING",
                effective_max_kw=effective_max,
                valid_min_kw=valid_min,
                priority_score=candidate.priority_score
            ))
            
    # Handle EVs that were not in candidates (departed, disconnected, target reached, etc.)
    for ev in state.evs:
        if ev.ev_id not in allocated_ev_ids:
            if ev.energy_required_kwh <= 0:
                status = "COMPLETE"
            elif ev.time_remaining_hours <= 0 or not ev.station_id:
                status = "PAUSED"
            else:
                status = "PAUSED" # Or maybe something else, but PAUSED is safe
                
            results.append(AllocationResult(
                ev_id=ev.ev_id,
                allocated_power_kw=0.0,
                status=status,
                effective_max_kw=0.0,
                valid_min_kw=0.0,
                priority_score=0.0
            ))
            
    return results
