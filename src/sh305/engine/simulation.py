import math
from sh305.domain.system_state import SystemState
from sh305.domain.enums import TimeOfDay, WeatherCondition
from sh305.engine.priority import WeightConfig
from sh305.engine.updater import update_state_allocation

def step_simulation(state: SystemState, step_hours: float = 0.25, weights: WeightConfig = None):
    if weights is None:
        weights = WeightConfig()
        
    # 7. update SoC using PREVIOUS allocation
    for ev in state.evs:
        if ev.station_id and ev.current_charging_rate_kw > 0.0:
            energy_added = ev.current_charging_rate_kw * step_hours
            soc_added = (energy_added / ev.battery_capacity_kwh) * 100.0
            ev.current_soc = min(100.0, ev.current_soc + soc_added)
            
            # When target SoC is reached, strictly halt charging rate.
            # Downstream allocation may do this as well, but we enforce the physical limit here.
            if ev.target_soc is not None and ev.current_soc >= ev.target_soc:
                ev.current_charging_rate_kw = 0.0
                
    # 1. advance time
    state.simulation.simulation_time += step_hours
    time = state.simulation.simulation_time
    
    # 2. determine weather/time-of-day
    # Basic deterministic thresholds for time of day
    time_modulo = time % 24.0
    if 6.0 <= time_modulo < 12.0:
        state.environment.time_of_day = TimeOfDay.MORNING
    elif 12.0 <= time_modulo < 17.0:
        state.environment.time_of_day = TimeOfDay.AFTERNOON
    elif 17.0 <= time_modulo < 20.0:
        state.environment.time_of_day = TimeOfDay.EVENING
    else:
        state.environment.time_of_day = TimeOfDay.NIGHT
        
    # 3. update building demand
    # Simple deterministic curves mimicking typical daily profiles
    state.building.lights_demand_kw = 10.0 if state.environment.time_of_day in (TimeOfDay.EVENING, TimeOfDay.NIGHT) else 2.0
    state.building.ac_demand_kw = 20.0 if state.environment.time_of_day == TimeOfDay.AFTERNOON else 5.0
    state.building.lifts_demand_kw = 15.0 if state.environment.time_of_day in (TimeOfDay.MORNING, TimeOfDay.EVENING) else 5.0
    state.building.appliances_demand_kw = 10.0
    
    state.building.total_demand_kw = sum([
        state.building.lights_demand_kw,
        state.building.ac_demand_kw,
        state.building.lifts_demand_kw,
        state.building.appliances_demand_kw,
        state.building.manual_demand_offset_kw
    ])
    
    # 4. update solar generation
    if state.environment.time_of_day == TimeOfDay.NIGHT or time_modulo < 6.0 or time_modulo > 18.0:
        state.solar.generation_kw = 0.0
    else:
        weather_factor = {
            WeatherCondition.SUNNY: 1.0,
            WeatherCondition.CLOUDY: 0.5,
            WeatherCondition.RAIN: 0.2
        }.get(state.environment.weather, 1.0)
        
        # Solar follows a sine wave from 6am to 6pm
        curve = math.sin((time_modulo - 6.0) / 12.0 * math.pi)
        base_solar_capacity = 100.0
        state.solar.generation_kw = max(0.0, base_solar_capacity * curve * weather_factor)

    # 5. process EV arrivals & 6. process EV departures
    for ev in state.evs:
        # Before arrival or after departure
        if time < ev.arrival_time or time >= ev.departure_time:
            ev.current_charging_rate_kw = 0.0
            if ev.station_id:
                # Free the station
                st = next((s for s in state.stations if s.station_id == ev.station_id), None)
                if st:
                    st.connected_ev_id = None
                    st.occupied = False
                ev.station_id = None
        else:
            # Inside the charging window (Arrived and not departed)
            if not ev.station_id:
                # Needs a station. Try to assign deterministically to the first available.
                available_stations = sorted([s for s in state.stations if not s.occupied], key=lambda x: x.station_id)
                if available_stations:
                    st = available_stations[0]
                    st.connected_ev_id = ev.ev_id
                    st.occupied = True
                    ev.station_id = st.station_id

    # 8, 9, 10. Recalculate requirements, priorities, and allocation
    # The existing update_state_allocation handles all of Phase 2 logic (requirements/energy) 
    # followed by Phase 3A (priority) and Phase 3B (optimization).
    update_state_allocation(state, weights, control_interval_hours=step_hours)


def run_24h_simulation(state: SystemState, step_hours: float = 0.25, weights: WeightConfig = None):
    # Reset to start of day
    state.simulation.simulation_time = 0.0
    
    # Make an initial state assessment at 0.0 so we have valid boundaries
    # before the first true physical step
    
    while state.simulation.simulation_time < 24.0:
        # Floating point safe check for terminal hour
        if 24.0 - state.simulation.simulation_time < (step_hours / 2.0):
            break
            
        step_simulation(state, step_hours, weights)
