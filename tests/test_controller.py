import pytest
from sh305.domain.system_state import SystemState
from sh305.domain.enums import TimeOfDay, WeatherCondition, SimulationStatus, VehicleType, UserUrgency
from sh305.domain.simulation import Simulation
from sh305.domain.environment import Environment, Solar
from sh305.domain.grid import Grid
from sh305.domain.building import Building
from sh305.domain.station import Station
from sh305.domain.ev import EV
from sh305.engine.controller import (
    apply_building_demand_delta,
    apply_grid_limit_delta,
    change_weather,
    spawn_ev,
    spawn_urgent_ev
)

@pytest.fixture
def base_state():
    return SystemState(
        simulation=Simulation(simulation_time=12.0, start_time=0.0, end_time=24.0, simulation_status=SimulationStatus.RUNNING),
        environment=Environment(weather=WeatherCondition.SUNNY, time_of_day=TimeOfDay.AFTERNOON),
        grid=Grid(configured_limit_kw=100.0, active_limit_kw=100.0, current_import_kw=0.0, available_capacity_kw=100.0),
        building=Building(ac_demand_kw=20.0, lights_demand_kw=2.0, lifts_demand_kw=5.0, appliances_demand_kw=10.0, total_demand_kw=37.0),
        solar=Solar(generation_kw=100.0, usable_solar_kw=0.0, excess_solar_kw=0.0), # Assuming midday sunny solar
        stations=[
            Station(station_id="CS-1", station_capacity_kw=22.0, max_charging_rate_kw=22.0, min_charging_rate_kw=1.0),
            Station(station_id="CS-2", station_capacity_kw=22.0, max_charging_rate_kw=22.0, min_charging_rate_kw=1.0)
        ],
        evs=[
            EV(
                ev_id="EV-1", station_id="CS-1", vehicle_type=VehicleType.SUV, 
                battery_capacity_kwh=60.0, expected_range_km=300.0, current_soc=50.0, 
                requested_travel_distance_km=150.0, arrival_time=8.0, departure_time=17.0, 
                max_charging_rate_kw=11.0, min_charging_rate_kw=1.0, user_urgency=UserUrgency.LOW,
            )
        ]
    )

def test_building_demand_change(base_state):
    initial_demand = base_state.building.total_demand_kw
    apply_building_demand_delta(base_state, 10.0)
    assert base_state.building.total_demand_kw == initial_demand + 10.0
    assert base_state.grid.current_import_kw <= base_state.grid.active_limit_kw

def test_grid_limit_change(base_state):
    initial_limit = base_state.grid.active_limit_kw
    apply_grid_limit_delta(base_state, -50.0)
    assert base_state.grid.active_limit_kw == initial_limit - 50.0
    assert base_state.grid.current_import_kw <= base_state.grid.active_limit_kw

def test_weather_change(base_state):
    initial_solar = base_state.solar.generation_kw
    change_weather(base_state, WeatherCondition.RAIN)
    assert base_state.environment.weather == WeatherCondition.RAIN
    assert base_state.solar.generation_kw < initial_solar
    assert base_state.grid.current_import_kw <= base_state.grid.active_limit_kw

def test_ev_spawn(base_state):
    base_state.stations[0].occupied = True
    ev = spawn_ev(base_state, urgency=UserUrgency.HIGH)
    assert ev is not None
    assert ev.user_urgency == UserUrgency.HIGH
    assert ev.station_id == "CS-2"
    assert base_state.stations[1].occupied == True
    assert base_state.grid.current_import_kw <= base_state.grid.active_limit_kw

def test_urgent_ev_spawn(base_state):
    ev = spawn_urgent_ev(base_state)
    assert ev.user_urgency == UserUrgency.CRITICAL
    assert base_state.grid.current_import_kw <= base_state.grid.active_limit_kw

def test_immediate_allocation_recomputation(base_state):
    apply_building_demand_delta(base_state, 160.0)
    assert base_state.grid.current_import_kw <= base_state.grid.active_limit_kw
    assert base_state.evs[0].current_charging_rate_kw < 11.0

def test_unavailable_station_handling(base_state):
    base_state.stations[0].occupied = True
    base_state.stations[1].occupied = True
    with pytest.raises(RuntimeError, match="No available stations"):
        spawn_ev(base_state)

def test_repeated_a1_actions(base_state):
    apply_building_demand_delta(base_state, 50.0)
    apply_grid_limit_delta(base_state, -20.0)
    change_weather(base_state, WeatherCondition.CLOUDY)
    spawn_urgent_ev(base_state)
    
    assert base_state.grid.current_import_kw <= base_state.grid.active_limit_kw
    assert len(base_state.evs) == 2
