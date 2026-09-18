import pytest
from sh305.domain.system_state import SystemState
from sh305.domain.enums import TimeOfDay, WeatherCondition, SimulationStatus, VehicleType, UserUrgency
from sh305.domain.simulation import Simulation
from sh305.domain.environment import Environment, Solar
from sh305.domain.grid import Grid
from sh305.domain.building import Building
from sh305.domain.station import Station
from sh305.domain.ev import EV
from sh305.engine.prediction import calculate_predictive_risk

@pytest.fixture
def base_state():
    return SystemState(
        simulation=Simulation(simulation_time=12.0, start_time=0.0, end_time=24.0, simulation_status=SimulationStatus.RUNNING),
        environment=Environment(weather=WeatherCondition.SUNNY, time_of_day=TimeOfDay.AFTERNOON),
        grid=Grid(configured_limit_kw=100.0, active_limit_kw=100.0, current_import_kw=0.0, available_capacity_kw=100.0),
        building=Building(ac_demand_kw=0.0, lights_demand_kw=0.0, lifts_demand_kw=0.0, appliances_demand_kw=10.0, total_demand_kw=10.0),
        solar=Solar(generation_kw=0.0, usable_solar_kw=0.0, excess_solar_kw=0.0),
        stations=[
            Station(station_id="CS-1", station_capacity_kw=22.0, max_charging_rate_kw=22.0, min_charging_rate_kw=1.0)
        ],
        evs=[
            EV(
                ev_id="EV-1", station_id="CS-1", vehicle_type=VehicleType.SUV, 
                battery_capacity_kwh=60.0, expected_range_km=300.0, current_soc=50.0, 
                requested_travel_distance_km=150.0, arrival_time=8.0, departure_time=13.0, 
                max_charging_rate_kw=11.0, min_charging_rate_kw=1.0, user_urgency=UserUrgency.LOW,
                current_charging_rate_kw=11.0, time_remaining_hours=1.0, target_soc=60.0
            )
        ]
    )

def test_risk_false_when_sufficient(base_state):
    # Target = 60.0%, current = 50.0%, charging rate = 11.0
    # Next 30 mins: 11.0 * 0.5 / 60 * 100 = 9.1666%
    # Remaining 0.5 hours: 11.0 * 0.5 / 60 * 100 = 9.1666%
    # Total potential SOC = 50.0 + 9.1666 + 9.1666 = 68.33% >= 60.0% -> Risk False
    calculate_predictive_risk(base_state)
    assert base_state.evs[0].predictive_risk_flag == False

def test_risk_true_when_insufficient(base_state):
    # Current rate = 4.0 (reduced rate)
    base_state.evs[0].current_charging_rate_kw = 4.0
    # Next 30 mins: 4.0 * 0.5 / 60 * 100 = 3.333%
    # Remaining 0.5 hours: 4.0 * 0.5 / 60 * 100 = 3.333%
    # Total potential SOC = 50.0 + 6.666 = 56.66% < 60.0% -> Risk True
    calculate_predictive_risk(base_state)
    assert base_state.evs[0].predictive_risk_flag == True

def test_risk_false_exact_boundary(base_state):
    # Target = 60.0, current rate = 6.0
    # 6.0 * 1.0 hr / 60 * 100 = 10.0%
    # 50.0 + 10.0 = 60.0% -> exactly on boundary -> Risk False
    base_state.evs[0].current_charging_rate_kw = 6.0
    base_state.evs[0].target_soc = 60.0
    calculate_predictive_risk(base_state)
    assert base_state.evs[0].predictive_risk_flag == False 
    
    # If target is 60.1, it should be True
    base_state.evs[0].target_soc = 60.1
    calculate_predictive_risk(base_state)
    assert base_state.evs[0].predictive_risk_flag == True

def test_less_than_30_minute_departure(base_state):
    # EV leaves in 0.25 hours (15 mins)
    base_state.evs[0].time_remaining_hours = 0.25
    base_state.evs[0].current_charging_rate_kw = 12.0
    # 12.0 * 0.25 / 60 * 100 = 5.0%
    # 50 + 5 = 55.0%
    base_state.evs[0].target_soc = 55.0
    calculate_predictive_risk(base_state)
    assert base_state.evs[0].predictive_risk_flag == False
    
    base_state.evs[0].target_soc = 56.0
    calculate_predictive_risk(base_state)
    assert base_state.evs[0].predictive_risk_flag == True

def test_risk_false_if_already_at_target(base_state):
    base_state.evs[0].current_soc = 100.0
    calculate_predictive_risk(base_state)
    assert base_state.evs[0].predictive_risk_flag == False

def test_risk_false_if_departed(base_state):
    base_state.evs[0].time_remaining_hours = 0.0
    calculate_predictive_risk(base_state)
    assert base_state.evs[0].predictive_risk_flag == False

def test_a3_uses_current_allocation_no_modify(base_state):
    import copy
    initial_rate = base_state.evs[0].current_charging_rate_kw
    calculate_predictive_risk(base_state)
    assert base_state.evs[0].current_charging_rate_kw == initial_rate
