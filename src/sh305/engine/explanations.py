from sh305.domain.system_state import SystemState

def generate_explanations(state: SystemState, control_interval_hours: float = 0.25):
    """
    A2: Explainable Charging Decision.
    Generates deterministic reason strings from actual current state without LLMs.
    """
    # Evaluate global factors
    available_capacity = max(0.0, state.grid.active_limit_kw - state.building.total_demand_kw + state.solar.generation_kw)
    total_requested = sum(
        ev.max_charging_rate_kw for ev in state.evs if ev.station_id and ev.energy_required_kwh > 0 and ev.time_remaining_hours > 0
    )
    grid_pressure = total_requested > available_capacity
    high_building_demand = state.building.total_demand_kw > (state.grid.active_limit_kw * 0.8)
    low_solar = state.solar.generation_kw < 10.0
    
    for ev in state.evs:
        if ev.target_soc is not None and ev.current_soc >= ev.target_soc:
            ev.reason = "Target reached."
            continue
            
        if not ev.station_id or ev.time_remaining_hours <= 0:
            ev.reason = "Disconnected or departed."
            continue
            
        station = next((s for s in state.stations if s.station_id == ev.station_id), None)
        if not station:
            continue
            
        effective_max = min(ev.max_charging_rate_kw, station.max_charging_rate_kw, station.station_capacity_kw)
        target_safe_power = ev.energy_required_kwh / control_interval_hours
        p_max = min(effective_max, target_safe_power)
        
        rate = ev.current_charging_rate_kw
        
        # State indicators
        reasons = []
        if ev.current_soc < 30.0:
            reasons.append("low SoC")
        if ev.time_remaining_hours < 2.0:
            reasons.append("close departure")
        if ev.required_average_power_kw > (effective_max * 0.8):
            reasons.append("high required power")
            
        if rate == 0.0:
            if ev.min_charging_rate_kw > available_capacity:
                ev.reason = "Charging paused because available capacity cannot meet minimum rate."
            elif grid_pressure:
                higher_pri = any(other.priority_score > ev.priority_score for other in state.evs if other.current_charging_rate_kw > 0)
                if higher_pri:
                    ev.reason = "Charging paused because a higher-priority EV claimed available power under grid pressure."
                else:
                    ev.reason = "Charging paused due to severe grid pressure and building demand."
            else:
                ev.reason = "Charging paused due to physical constraints."
        
        elif rate < p_max - 0.01: # reduced
            if grid_pressure:
                higher_pri = any(other.priority_score > ev.priority_score for other in state.evs if other.current_charging_rate_kw > rate)
                factors = []
                if high_building_demand: factors.append("building demand increased")
                if low_solar: factors.append("solar is reduced")
                if higher_pri: factors.append("a higher-priority EV has greater precedence")
                
                if factors:
                    ev.reason = f"Charging reduced because {' while '.join(factors)}."
                else:
                    ev.reason = "Charging reduced due to grid pressure."
            else:
                ev.reason = "Charging reduced due to station or target-safe bounds."
                
        else:
            msg = "Allocated optimal power"
            if reasons:
                msg += f" due to {', '.join(reasons)}."
            else:
                msg += "."
            ev.reason = msg
