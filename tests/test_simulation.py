import pytest
from sh305.domain.system_state import SystemState
from sh305.domain.enums import TimeOfDay, WeatherCondition, SimulationStatus, VehicleType, UserUrgency
from sh305.domain.simulation import Simulation
from sh305.domain.environment import Environment, Solar
from sh305.domain.grid import Grid
from sh305.domain.building import Building
from sh305.domain.station import Station
from sh305.domain.ev import EV
from sh305.engine.simulation import step_simulation, run_24h_simulation
from sh305.engine.priority import WeightConfig
import copy

@pytest.fixture
def base_state():
    return SystemState(
        simulation=Simulation(simulation_time=0.0, start_time=0.0, end_time=24.0, simulation_status=SimulationStatus.RUNNING),
        environment=Environment(weather=WeatherCondition.SUNNY, time_of_day=TimeOfDay.NIGHT),
        grid=Grid(configured_limit_kw=100.0, active_limit_kw=100.0, current_import_kw=0.0, available_capacity_kw=100.0),
        building=Building(ac_demand_kw=0.0, lights_demand_kw=0.0, lifts_demand_kw=0.0, appliances_demand_kw=10.0, total_demand_kw=10.0),
        solar=Solar(generation_kw=0.0, usable_solar_kw=0.0, excess_solar_kw=0.0),
        stations=[
            Station(station_id="CS-1", station_capacity_kw=22.0, max_charging_rate_kw=22.0, min_charging_rate_kw=1.0)
        ],
        evs=[
            EV(
                ev_id="EV-1", station_id=None, vehicle_type=VehicleType.SUV, 
                battery_capacity_kwh=60.0, expected_range_km=300.0, current_soc=50.0, 
                requested_travel_distance_km=150.0, arrival_time=8.0, departure_time=17.0, 
                max_charging_rate_kw=11.0, min_charging_rate_kw=1.0, user_urgency=UserUrgency.CRITICAL,
            )
        ]
    )

def test_time_advances(base_state):
    step_simulation(base_state, 0.25)
    assert base_state.simulation.simulation_time == 0.25
    
def test_night_solar_zero(base_state):
    base_state.simulation.simulation_time = 2.0
    step_simulation(base_state, 0.25)
    assert base_state.solar.generation_kw == 0.0
    
def test_solar_rises_and_falls(base_state):
    base_state.simulation.simulation_time = 7.75
    step_simulation(base_state, 0.25)
    solar_8 = base_state.solar.generation_kw
    assert solar_8 > 0.0
    
    base_state.simulation.simulation_time = 11.75
    step_simulation(base_state, 0.25)
    solar_12 = base_state.solar.generation_kw
    assert solar_12 > solar_8
    
    base_state.simulation.simulation_time = 16.75
    step_simulation(base_state, 0.25)
    solar_17 = base_state.solar.generation_kw
    assert solar_17 < solar_12
    
def test_weather_affects_solar(base_state):
    base_state.simulation.simulation_time = 11.75
    step_simulation(base_state, 0.25)
    sunny_solar = base_state.solar.generation_kw
    
    base_state.simulation.simulation_time = 11.75
    base_state.environment.weather = WeatherCondition.CLOUDY
    step_simulation(base_state, 0.25)
    cloudy_solar = base_state.solar.generation_kw
    
    assert cloudy_solar < sunny_solar

def test_building_demand_changes(base_state):
    base_state.simulation.simulation_time = 3.75
    step_simulation(base_state, 0.25)
    night_demand = base_state.building.total_demand_kw
    
    base_state.simulation.simulation_time = 13.75
    step_simulation(base_state, 0.25)
    afternoon_demand = base_state.building.total_demand_kw
    
    assert night_demand != afternoon_demand
    
def test_ev_arrival_departure_occupancy(base_state):
    ev = base_state.evs[0]
    st = base_state.stations[0]
    
    # Before arrival
    base_state.simulation.simulation_time = 7.75
    step_simulation(base_state, 0.25) # now 8.0
    assert ev.station_id == "CS-1"
    assert st.occupied == True
    
    # After departure
    base_state.simulation.simulation_time = 16.75
    step_simulation(base_state, 0.25) # now 17.0
    assert ev.station_id is None
    assert st.occupied == False
    
def test_soc_progression_and_target_stops(base_state):
    ev = base_state.evs[0]
    ev.current_soc = 50.0
    ev.arrival_time = 0.0
    ev.departure_time = 10.0
    ev.requested_travel_distance_km = 300.0 # target_soc = 100%
    
    base_state.simulation.simulation_time = 0.0
    # First step will assign charging
    step_simulation(base_state, 1.0)
    
    # step again to apply charging
    step_simulation(base_state, 1.0)
    assert ev.current_soc > 50.0
    assert ev.current_soc <= 100.0
    
    # wait until fully charged
    while ev.current_soc < 100.0 and base_state.simulation.simulation_time < 9.0:
        step_simulation(base_state, 0.25)
        
    assert ev.current_soc == 100.0
    assert ev.current_charging_rate_kw == 0.0
    
def test_deterministic_repeated_simulation(base_state):
    state_copy = copy.deepcopy(base_state)
    
    run_24h_simulation(base_state)
    soc1 = base_state.evs[0].current_soc
    
    run_24h_simulation(state_copy)
    soc2 = state_copy.evs[0].current_soc
    
    assert soc1 == soc2
