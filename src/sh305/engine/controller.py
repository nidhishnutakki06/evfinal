import math
from sh305.domain.system_state import SystemState
from sh305.domain.enums import WeatherCondition, UserUrgency, VehicleType, TimeOfDay
from sh305.domain.ev import EV
from sh305.engine.priority import WeightConfig, STRATEGY_WEIGHTS
from sh305.engine.updater import update_state_allocation

def _recompute(state: SystemState, step_hours: float = 0.25, weights: WeightConfig = None):
    """
    Immediate recomputation pipeline.
    Applies the Phase 2, Phase 3A, and Phase 3B sequence to the current state.
    """
    if weights is None:
        strategy_name = state.strategy if state.strategy in STRATEGY_WEIGHTS else "BALANCED"
        weights = STRATEGY_WEIGHTS.get(strategy_name, WeightConfig())
    update_state_allocation(state, weights, control_interval_hours=step_hours)


def set_strategy(state: SystemState, strategy: str, step_hours: float = 0.25):
    """
    A4 Control: Switch the global allocation strategy and immediately recompute.
    """
    if strategy not in STRATEGY_WEIGHTS:
        raise ValueError(f"Unknown strategy: {strategy}")
    state.strategy = strategy
    weights = STRATEGY_WEIGHTS[strategy]
    _recompute(state, step_hours, weights)


def apply_building_demand_delta(state: SystemState, delta_kw: float, step_hours: float = 0.25, weights: WeightConfig = None):
    """
    A1 Control: Adjust building demand by a delta, recalculating bounds immediately.
    """
    # Accumulate into manual_demand_offset_kw to maintain structural parity without overriding rigid time-curves
    state.building.manual_demand_offset_kw += delta_kw
    state.building.total_demand_kw = sum([
        state.building.lights_demand_kw,
        state.building.ac_demand_kw,
        state.building.lifts_demand_kw,
        state.building.appliances_demand_kw,
        state.building.manual_demand_offset_kw
    ])
    _recompute(state, step_hours, weights)


def apply_grid_limit_delta(state: SystemState, delta_kw: float, step_hours: float = 0.25, weights: WeightConfig = None):
    """
    A1 Control: Adjust the active grid capacity limit by a delta, bounded strictly above zero.
    """
    new_limit = max(0.1, state.grid.active_limit_kw + delta_kw)
    state.grid.active_limit_kw = new_limit
    _recompute(state, step_hours, weights)


def change_weather(state: SystemState, weather: WeatherCondition, step_hours: float = 0.25, weights: WeightConfig = None):
    """
    A1 Control: Set active weather condition, update synthetic solar output, and re-allocate.
    """
    state.environment.weather = weather
    
    time = state.simulation.simulation_time
    time_modulo = time % 24.0
    
    if state.environment.time_of_day == TimeOfDay.NIGHT or time_modulo < 6.0 or time_modulo > 18.0:
        state.solar.generation_kw = 0.0
    else:
        weather_factor = {
            WeatherCondition.SUNNY: 1.0,
            WeatherCondition.CLOUDY: 0.5,
            WeatherCondition.RAIN: 0.2
        }.get(weather, 1.0)
        
        curve = math.sin((time_modulo - 6.0) / 12.0 * math.pi)
        base_solar_capacity = 100.0
        state.solar.generation_kw = max(0.0, base_solar_capacity * curve * weather_factor)
        
    _recompute(state, step_hours, weights)


def _generate_synthetic_ev_id(state: SystemState) -> str:
    max_id = 0
    for ev in state.evs:
        if ev.ev_id.startswith("EV-"):
            try:
                num = int(ev.ev_id.split("-")[1])
                if num > max_id:
                    max_id = num
            except ValueError:
                pass
    return f"EV-{max_id + 1}"


def spawn_ev(state: SystemState, urgency: UserUrgency = UserUrgency.MEDIUM, step_hours: float = 0.25, weights: WeightConfig = None) -> EV:
    """
    A1 Control: Spawns a new synthetic EV dynamically and connects it to an available station.
    """
    time = state.simulation.simulation_time
    
    available_stations = sorted([s for s in state.stations if not s.occupied], key=lambda x: x.station_id)
    if not available_stations:
        raise RuntimeError("No available stations to spawn EV")
        
    st = available_stations[0]
    
    new_ev = EV(
        ev_id=_generate_synthetic_ev_id(state),
        station_id=st.station_id,
        vehicle_type=VehicleType.SUV,
        battery_capacity_kwh=60.0,
        expected_range_km=300.0,
        current_soc=20.0,
        requested_travel_distance_km=100.0,
        arrival_time=time,
        departure_time=time + 8.0,
        max_charging_rate_kw=11.0,
        min_charging_rate_kw=1.0,
        user_urgency=urgency
    )
    
    st.connected_ev_id = new_ev.ev_id
    st.occupied = True
    
    state.evs.append(new_ev)
    _recompute(state, step_hours, weights)
    
    return new_ev


def spawn_urgent_ev(state: SystemState, step_hours: float = 0.25, weights: WeightConfig = None) -> EV:
    """
    A1 Control: Shortcut to spawn a CRITICAL urgency EV immediately.
    """
    return spawn_ev(state, urgency=UserUrgency.CRITICAL, step_hours=step_hours, weights=weights)


def activate_emergency(state: SystemState, reduction_fraction: float = 0.40, step_hours: float = 0.25, weights: WeightConfig = None):
    """
    A5 Control: Activate emergency mode, curtailing the active grid limit by a fraction,
    and triggering an immediate re-allocation which automatically pauses lower priority
    EVs that cannot meet their valid minimums.
    """
    state.emergency = True
    state.grid.emergency_mode = True
    # Emergency limit is applied against the configured (contractual) limit
    state.grid.active_limit_kw = state.grid.configured_limit_kw * (1.0 - reduction_fraction)
    _recompute(state, step_hours, weights)


def restore_grid(state: SystemState, step_hours: float = 0.25, weights: WeightConfig = None):
    """
    A5 Control: Restore normal grid operation by releasing the emergency limit
    and immediately re-allocating power to resume EVs according to priority.
    """
    state.emergency = False
    state.grid.emergency_mode = False
    state.grid.active_limit_kw = state.grid.configured_limit_kw
    _recompute(state, step_hours, weights)
