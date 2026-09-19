import pytest
from sh305.domain.ev import EV
from sh305.domain.station import Station
from sh305.domain.system_state import SystemState
from sh305.domain.enums import VehicleType, UserUrgency, WeatherCondition, TimeOfDay, SimulationStatus
from sh305.domain.simulation import Simulation
from sh305.domain.environment import Environment, Solar
from sh305.domain.grid import Grid
from sh305.domain.building import Building
from sh305.engine.priority import WeightConfig, identify_candidates, Candidate
from sh305.engine.optimizer import allocate_charging, AllocationResult
from sh305.engine.updater import update_state_allocation

@pytest.fixture
def base_state():
    return SystemState(
        simulation=Simulation(simulation_time=8.0, start_time=0.0, end_time=24.0, simulation_status=SimulationStatus.RUNNING),
        environment=Environment(weather=WeatherCondition.SUNNY, time_of_day=TimeOfDay.MORNING),
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
                battery_capacity_kwh=60.0, expected_range_km=300.0, current_soc=20.0, 
                requested_travel_distance_km=150.0, arrival_time=8.0, departure_time=17.0, 
                max_charging_rate_kw=11.0, min_charging_rate_kw=1.0, user_urgency=UserUrgency.CRITICAL,
            ),
            EV(
                ev_id="EV-2", station_id="CS-2", vehicle_type=VehicleType.SEDAN, 
                battery_capacity_kwh=60.0, expected_range_km=300.0, current_soc=80.0, 
                requested_travel_distance_km=50.0, arrival_time=8.0, departure_time=17.0, 
                max_charging_rate_kw=11.0, min_charging_rate_kw=1.0, user_urgency=UserUrgency.LOW,
            )
        ]
    )

def test_normal_capacity(base_state):
    weights = WeightConfig()
    update_state_allocation(base_state, weights)
    
    # Building=10, Grid=100 -> Available=90
    # Both EV1 and EV2 want to charge. EV1 requires (50-20)=18kWh. Target safe power = 18/0.25 = 72kW. P_max = min(11, 22, 72)=11.
    # EV2 requires (16.66+10)=26.66, target is 26.66%. Wait, 80% is above target! Target is likely ~26%.
    # If target < 80%, energy_req = 0.
    
    ev1 = base_state.evs[0]
    ev2 = base_state.evs[1]
    
    # Force both to need energy
    ev1.current_soc = 10.0
    ev2.current_soc = 10.0
    ev2.requested_travel_distance_km = 150.0
    
    update_state_allocation(base_state, weights)
    
    assert ev1.current_charging_rate_kw == 11.0
    assert ev2.current_charging_rate_kw == 11.0
    assert base_state.grid.current_import_kw == 10.0 + 11.0 + 11.0
    
def test_grid_constrained_case(base_state):
    base_state.grid.active_limit_kw = 25.0
    # Building 10. Available grid = 15.0
    ev1 = base_state.evs[0]
    ev2 = base_state.evs[1]
    ev1.current_soc = 10.0
    ev2.current_soc = 10.0
    ev2.requested_travel_distance_km = 150.0
    
    weights = WeightConfig()
    update_state_allocation(base_state, weights)
    
    # Priority: EV1 (CRITICAL) vs EV2 (LOW). EV1 gets 11.0 kW. Remaining = 15 - 11 = 4.0 kW
    assert ev1.current_charging_rate_kw == 11.0
    assert ev2.current_charging_rate_kw == 4.0
    assert base_state.grid.current_import_kw == 25.0

def test_minimum_rate_conflict(base_state):
    base_state.grid.active_limit_kw = 25.0
    ev1 = base_state.evs[0]
    ev2 = base_state.evs[1]
    ev1.current_soc = 10.0
    ev2.current_soc = 10.0
    ev2.requested_travel_distance_km = 150.0
    
    # EV2 has valid minimum of 5.0
    ev2.min_charging_rate_kw = 5.0
    
    weights = WeightConfig()
    update_state_allocation(base_state, weights)
    
    # EV1 gets 11.0. Remaining = 4.0. EV2 min = 5.0 > 4.0. EV2 gets paused.
    assert ev1.current_charging_rate_kw == 11.0
    assert ev2.current_charging_rate_kw == 0.0

def test_station_bottleneck(base_state):
    ev1 = base_state.evs[0]
    ev1.current_soc = 10.0
    ev1.max_charging_rate_kw = 50.0
    base_state.stations[0].station_capacity_kw = 7.0
    
    weights = WeightConfig()
    update_state_allocation(base_state, weights)
    
    assert ev1.current_charging_rate_kw == 7.0

def test_target_nearly_reached(base_state):
    ev1 = base_state.evs[0]
    ev1.current_soc = 49.0
    # Travel need 150km on 300km range -> 50% + 10% reserve = 60%
    ev1.requested_travel_distance_km = 150.0
    ev1.current_soc = 59.5
    # energy req = 0.5% of 60kWh = 0.3kWh
    # target safe power = 0.3 / 0.25 = 1.2 kW
    weights = WeightConfig()
    update_state_allocation(base_state, weights)
    
    assert ev1.current_charging_rate_kw == 1.2

def test_physical_feasible_current_infeasible_case(base_state):
    ev1 = base_state.evs[0]
    ev1.current_soc = 10.0
    ev1.departure_time = 8.5 # 0.5h remaining
    ev1.energy_required_kwh = 5.0 # Pre-set doesn't matter, it's calculated
    
    weights = WeightConfig()
    update_state_allocation(base_state, weights)
    assert ev1.current_charging_rate_kw > 0
    # We mainly test it doesn't crash and allocates

def test_disconnected_departed_ev(base_state):
    ev1 = base_state.evs[0]
    ev1.station_id = None # Disconnected
    ev2 = base_state.evs[1]
    ev2.departure_time = 7.0 # Departed
    
    weights = WeightConfig()
    update_state_allocation(base_state, weights)
    
    assert ev1.current_charging_rate_kw == 0.0
    assert ev2.current_charging_rate_kw == 0.0

def test_no_evs(base_state):
    base_state.evs = []
    weights = WeightConfig()
    update_state_allocation(base_state, weights)
    assert base_state.grid.current_import_kw == 10.0

def test_deterministic_repeated_run(base_state):
    base_state.evs[0].current_soc = 10.0
    base_state.evs[1].current_soc = 10.0
    base_state.grid.active_limit_kw = 25.0
    weights = WeightConfig()
    
    update_state_allocation(base_state, weights)
    rate1_1, rate2_1 = base_state.evs[0].current_charging_rate_kw, base_state.evs[1].current_charging_rate_kw
    
    # Reset and run again
    base_state.evs[0].current_charging_rate_kw = 0.0
    base_state.evs[1].current_charging_rate_kw = 0.0
    update_state_allocation(base_state, weights)
    rate1_2, rate2_2 = base_state.evs[0].current_charging_rate_kw, base_state.evs[1].current_charging_rate_kw
    
    assert rate1_1 == rate1_2
    assert rate2_1 == rate2_2

def test_tie_breaking(base_state):
    base_state.grid.active_limit_kw = 15.0 # building 10, remaining 5
    ev1 = base_state.evs[0]
    ev2 = base_state.evs[1]
    # Make them identical
    ev1.user_urgency = UserUrgency.MEDIUM
    ev2.user_urgency = UserUrgency.MEDIUM
    ev1.current_soc = 10.0
    ev2.current_soc = 10.0
    ev1.requested_travel_distance_km = 150.0
    ev2.requested_travel_distance_km = 150.0
    
    weights = WeightConfig()
    update_state_allocation(base_state, weights)
    
    # Priority is tied. ev_id tiebreak: EV-1 wins
    assert ev1.current_charging_rate_kw == 5.0
    assert ev2.current_charging_rate_kw == 0.0

def test_solar_headroom(base_state):
    # Building = 20, Solar = 50, Grid limit = 100
    base_state.building.total_demand_kw = 20.0
    base_state.solar.generation_kw = 50.0
    base_state.grid.active_limit_kw = 100.0
    
    ev1 = base_state.evs[0]
    ev1.current_soc = 10.0
    # Allow a very high max rate to consume all available capacity
    ev1.max_charging_rate_kw = 200.0
    base_state.stations[0].max_charging_rate_kw = 200.0
    base_state.stations[0].station_capacity_kw = 200.0
    # 130kW available (100 - 20 + 50)
    # Energy required: (50-10) * 60 / 100 = 24kWh
    # Target safe power = 24 / 0.25 = 96 kW.
    # We should artificially inflate energy_required to test full 130kW.
    # Target SOC = 100% -> Energy required = 90% of 60 = 54 kWh
    # Target safe = 54 / 0.25 = 216 kW
    ev1.requested_travel_distance_km = 300.0 # forces target_soc to 100% (reserve pushes it over, capped at 100)
    
    # EV2 departs so it does not consume power
    base_state.evs[1].departure_time = 7.0 
    
    weights = WeightConfig()
    update_state_allocation(base_state, weights)
    
    assert ev1.current_charging_rate_kw == 130.0

def test_solar_exceeds_site_load(base_state):
    # Building = 10, Solar = 50, Grid limit = 100
    base_state.building.total_demand_kw = 10.0
    base_state.solar.generation_kw = 50.0
    base_state.grid.active_limit_kw = 100.0
    
    ev1 = base_state.evs[0]
    ev1.current_soc = 10.0
    # Travel distance -> Target SOC -> energy
    ev1.requested_travel_distance_km = 15.0 # (15/300) = 5% + 10% = 15% -> target=20% -> requires very little energy, so it will hit target safe power
    # Actually, we just need to ensure grid_import == 0 and excess_solar > 0
    # Let's give it a normal EV
    ev1.max_charging_rate_kw = 11.0
    base_state.evs[1].departure_time = 7.0
    
    weights = WeightConfig()
    update_state_allocation(base_state, weights)
    
    # Site load = 10 (building) + 11 (EV) = 21
    # Usable solar = min(50, 21) = 21
    # Grid import = max(0, 21 - 21) = 0
    # Excess solar = 50 - 21 = 29
    assert base_state.grid.current_import_kw == 0.0
    assert base_state.solar.excess_solar_kw > 0.0
