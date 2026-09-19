from sh305.domain.system_state import SystemState

def calculate_predictive_risk(state: SystemState):
    """
    A3: 30-Minute Predictive Risk.
    Determines if an EV is on a trajectory capable of reaching its target by departure, 
    assuming the CURRENT allocation continues for the next 30 minutes.
    """
    for ev in state.evs:
        # If departed or not connected
        if not ev.station_id or ev.time_remaining_hours <= 0:
            ev.predictive_risk_flag = False
            continue
            
        # Already reached target
        if ev.target_soc is not None and ev.current_soc >= ev.target_soc:
            ev.predictive_risk_flag = False
            continue
            
        # Project next 30 minutes (0.5 hours) or until departure if less than 30 minutes
        first_period = min(0.5, ev.time_remaining_hours)
        soc_added_30m = (ev.current_charging_rate_kw * first_period / ev.battery_capacity_kwh) * 100.0
        projected_soc = ev.current_soc + soc_added_30m
        
        # Determine remaining time after those 30 minutes
        time_left_after_30m = max(0.0, ev.time_remaining_hours - 0.5)
        
        # A3 Rule Correction: What happens if CURRENT allocation continues?
        # Do NOT use max charging. Use current rate for the remaining time.
        projected_final_soc = projected_soc + (
            ev.current_charging_rate_kw
            * time_left_after_30m
            / ev.battery_capacity_kwh
            * 100.0
        )
        projected_final_soc = min(100.0, projected_final_soc)
        
        if ev.target_soc is not None and projected_final_soc < ev.target_soc:
            ev.predictive_risk_flag = True
        else:
            ev.predictive_risk_flag = False
