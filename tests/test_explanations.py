import pytest
from sh305.domain.system_state import SystemState
from sh305.domain.enums import TimeOfDay, WeatherCondition, SimulationStatus, VehicleType, UserUrgency
from sh305.domain.simulation import Simulation
from sh305.domain.environment import Environment, Solar
from sh305.domain.grid import Grid
from sh305.domain.building import Building
from sh305.domain.station import Station
from sh305.domain.ev import EV
from sh305.engine.explanations import generate_explanations
from sh305.engine.updater import update_state_allocation
from sh305.engine.priority import WeightConfig

@pytest.fixture
def base_state():
    return SystemState(
        simulation=Simulation(simulation_time=12.0, start_time=0.0, end_time=24.0, simulation_status=SimulationStatus.RUNNING),
        environment=Environment(weather=WeatherCondition.SUNNY, time_of_day=TimeOfDay.AFTERNOON),
        grid=Grid(configured_limit_kw=100.0, active_limit_kw=100.0, current_import_kw=0.0, available_capacity_kw=100.0),
        building=Building(ac_demand_kw=0.0, lights_demand_kw=0.0, lifts_demand_kw=0.0, appliances_demand_kw=10.0, total_demand_kw=10.0),
        solar=Solar(generation_kw=0.0, usable_solar_kw=0.0, excess_solar_kw=0.0),
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
            ),
            EV(
                ev_id="EV-2", station_id="CS-2", vehicle_type=VehicleType.SUV, 
                battery_capacity_kwh=60.0, expected_range_km=300.0, current_soc=50.0, 
                requested_travel_distance_km=150.0, arrival_time=8.0, departure_time=17.0, 
                max_charging_rate_kw=11.0, min_charging_rate_kw=1.0, user_urgency=UserUrgency.CRITICAL,
            )
        ]
    )

def test_target_reached_explanation(base_state):
    base_state.evs[0].current_soc = 100.0
    update_state_allocation(base_state, WeightConfig())
    assert "Target reached" in base_state.evs[0].reason

def test_optimal_allocation_explanation(base_state):
    update_state_allocation(base_state, WeightConfig())
    assert "Allocated optimal power" in base_state.evs[0].reason
    assert "Allocated optimal power" in base_state.evs[1].reason

def test_reduced_allocation_explanation(base_state):
    # 22kW total requested. Set grid limit such that available is ~15kW
    # Grid limit 25, building 10 -> 15 available. EV2 (Critical) gets 11, EV1 gets 4.
    base_state.solar.generation_kw = 10.0 # prevent "reduced solar" reason, but keep it low
    base_state.grid.active_limit_kw = 15.0
    update_state_allocation(base_state, WeightConfig())
    
    assert base_state.evs[1].current_charging_rate_kw == 11.0
    assert base_state.evs[0].current_charging_rate_kw == 4.0
    
    assert "Allocated optimal power" in base_state.evs[1].reason
    assert "Charging reduced" in base_state.evs[0].reason

def test_paused_allocation_explanation(base_state):
    # Valid min is 5.0 for EV1, but available is 4.0 -> EV1 paused
    base_state.evs[0].min_charging_rate_kw = 5.0
    base_state.grid.active_limit_kw = 25.0
    update_state_allocation(base_state, WeightConfig())
    
    assert base_state.evs[0].current_charging_rate_kw == 0.0
    assert "Charging paused" in base_state.evs[0].reason

def test_deterministic_repeat_explanations(base_state):
    import copy
    state_copy = copy.deepcopy(base_state)
    
    update_state_allocation(base_state, WeightConfig())
    update_state_allocation(state_copy, WeightConfig())
    
    assert base_state.evs[0].reason == state_copy.evs[0].reason
