import pytest
from sh305.domain.ev import EV
from sh305.domain.station import Station
from sh305.domain.system_state import SystemState
from sh305.domain.enums import VehicleType, UserUrgency, WeatherCondition, TimeOfDay, SimulationStatus
from sh305.domain.simulation import Simulation
from sh305.domain.environment import Environment, Solar
from sh305.domain.grid import Grid
from sh305.domain.building import Building
from sh305.engine import priority

@pytest.fixture
def base_ev():
    return EV(
        ev_id="EV-1",
        vehicle_type=VehicleType.SUV,
        battery_capacity_kwh=60.0,
        expected_range_km=300.0,
        current_soc=50.0,
        requested_travel_distance_km=150.0,
        arrival_time=8.0,
        departure_time=17.0,
        max_charging_rate_kw=11.0,
        min_charging_rate_kw=1.0,
        user_urgency=UserUrgency.MEDIUM
    )

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
        ],
        evs=[
            EV(
                ev_id="EV-1", station_id="CS-1", vehicle_type=VehicleType.SUV, 
                battery_capacity_kwh=60.0, expected_range_km=300.0, current_soc=20.0, 
                requested_travel_distance_km=150.0, arrival_time=8.0, departure_time=17.0, 
                max_charging_rate_kw=22.0, min_charging_rate_kw=1.0, user_urgency=UserUrgency.CRITICAL,
                energy_required_kwh=20.0, time_remaining_hours=4.0
            )
        ]
    )

# 1. every factor stays within [0,1]
def test_factors_bounded(base_ev):
    base_ev.current_soc = -10.0
    assert priority.calc_soc_urgency(base_ev) == 1.0
    base_ev.current_soc = 150.0
    assert priority.calc_soc_urgency(base_ev) == 0.0

# 2. lower SoC produces greater SoC urgency
def test_lower_soc_higher_urgency(base_ev):
    base_ev.current_soc = 20.0
    urgency_low = priority.calc_soc_urgency(base_ev)
    base_ev.current_soc = 80.0
    urgency_high = priority.calc_soc_urgency(base_ev)
    assert urgency_low > urgency_high

# 3. earlier departure produces greater deadline urgency
def test_earlier_departure_higher_urgency(base_ev):
    base_ev.time_remaining_hours = 2.0
    urgency_early = priority.calc_deadline_urgency(base_ev)
    base_ev.time_remaining_hours = 8.0
    urgency_late = priority.calc_deadline_urgency(base_ev)
    assert urgency_early > urgency_late

# 4. less remaining time produces greater time pressure
def test_less_time_greater_pressure(base_ev):
    base_ev.time_remaining_hours = 1.0
    pressure_high = priority.calc_time_urgency(base_ev)
    base_ev.time_remaining_hours = 3.0
    pressure_low = priority.calc_time_urgency(base_ev)
    assert pressure_high > pressure_low
    
# 5. greater energy requirement produces greater energy factor
def test_greater_energy_requirement_higher_factor(base_ev):
    base_ev.energy_required_kwh = 50.0
    req_high = priority.calc_energy_need(base_ev)
    base_ev.energy_required_kwh = 10.0
    req_low = priority.calc_energy_need(base_ev)
    assert req_high > req_low

# 6. greater required-power pressure produces greater pressure
def test_greater_required_power_pressure(base_ev):
    base_ev.required_average_power_kw = 10.0
    press_high = priority.calc_required_power_pressure(base_ev, effective_max_kw=11.0)
    base_ev.required_average_power_kw = 2.0
    press_low = priority.calc_required_power_pressure(base_ev, effective_max_kw=11.0)
    assert press_high > press_low

# 7. HIGH urgency > LOW urgency
def test_user_urgency_ordering(base_ev):
    base_ev.user_urgency = UserUrgency.HIGH
    score_high = priority.calc_user_urgency(base_ev)
    base_ev.user_urgency = UserUrgency.LOW
    score_low = priority.calc_user_urgency(base_ev)
    assert score_high > score_low

# 8. feasibility pressure responds to current-allocation feasibility
def test_feasibility_pressure(base_ev):
    base_ev.physical_feasibility = True
    base_ev.current_allocation_feasibility = False
    assert priority.calc_feasibility_pressure(base_ev) == 1.0
    base_ev.physical_feasibility = True
    base_ev.current_allocation_feasibility = True
    assert priority.calc_feasibility_pressure(base_ev) == 0.0

# 9. greater travel need produces greater travel factor
def test_greater_travel_need_greater_factor(base_ev):
    base_ev.requested_travel_distance_km = 300.0
    need_high = priority.calc_travel_need(base_ev)
    base_ev.requested_travel_distance_km = 50.0
    need_low = priority.calc_travel_need(base_ev)
    assert need_high > need_low

# 10. score is deterministic
def test_priority_score_deterministic(base_ev):
    base_ev.current_soc = 20.0
    base_ev.time_remaining_hours = 4.0
    base_ev.energy_required_kwh = 20.0
    base_ev.required_average_power_kw = 5.0
    weights = priority.WeightConfig()
    score1 = priority.calculate_priority_score(base_ev, effective_max_kw=11.0, weights=weights)
    score2 = priority.calculate_priority_score(base_ev, effective_max_kw=11.0, weights=weights)
    assert score1 == score2

# 11. deterministic tie-breaking works
def test_deterministic_tie_breaking():
    ev1 = EV(ev_id="EV-1", vehicle_type=VehicleType.SUV, battery_capacity_kwh=60.0, current_soc=50.0, expected_range_km=300.0, requested_travel_distance_km=0, arrival_time=8.0, departure_time=17.0, max_charging_rate_kw=11.0, min_charging_rate_kw=1.0, user_urgency=UserUrgency.MEDIUM)
    ev2 = EV(ev_id="EV-2", vehicle_type=VehicleType.SUV, battery_capacity_kwh=60.0, current_soc=50.0, expected_range_km=300.0, requested_travel_distance_km=0, arrival_time=8.0, departure_time=17.0, max_charging_rate_kw=11.0, min_charging_rate_kw=1.0, user_urgency=UserUrgency.MEDIUM)
    station = Station(station_id="CS-1", station_capacity_kw=22.0, max_charging_rate_kw=22.0, min_charging_rate_kw=1.0)
    
    c1 = priority.Candidate(ev=ev1, station=station, effective_max_kw=11.0, valid_min_kw=1.0, target_safe_power_kw=11.0, p_max=11.0, factors=priority.calculate_priority_factors(ev1, 11.0), priority_score=10.0)
    c2 = priority.Candidate(ev=ev2, station=station, effective_max_kw=11.0, valid_min_kw=1.0, target_safe_power_kw=11.0, p_max=11.0, factors=priority.calculate_priority_factors(ev2, 11.0), priority_score=10.0)
    
    # Priority same, departure same, soc same, ev_id should break tie EV-1 before EV-2
    sorted_candidates = priority.sort_candidates([c2, c1])
    assert sorted_candidates[0].ev.ev_id == "EV-1"
    assert sorted_candidates[1].ev.ev_id == "EV-2"

# 12. weights affect score as expected
def test_weights_affect_score(base_ev):
    base_ev.current_soc = 0.0 # soc_urgency = 1.0
    base_ev.time_remaining_hours = 24.0 # deadline_urgency=0, time_urgency=0
    base_ev.energy_required_kwh = 0.0
    base_ev.required_average_power_kw = 0.0
    base_ev.requested_travel_distance_km = 0.0
    base_ev.user_urgency = UserUrgency.LOW # 0.25
    
    weights1 = priority.WeightConfig(w_soc=1.0, w_user=0.0)
    score1 = priority.calculate_priority_score(base_ev, effective_max_kw=11.0, weights=weights1)
    
    weights2 = priority.WeightConfig(w_soc=2.0, w_user=0.0)
    score2 = priority.calculate_priority_score(base_ev, effective_max_kw=11.0, weights=weights2)
    
    assert score2 > score1

# 13. target-safe power uses control interval, not total remaining time
def test_target_safe_power(base_state):
    ev1 = base_state.evs[0]
    ev1.energy_required_kwh = 2.0
    ev1.time_remaining_hours = 4.0
    
    weights = priority.WeightConfig()
    candidates = priority.identify_candidates(base_state, weights, control_interval_hours=0.25)
    c = candidates[0]
    
    # target_safe = 2.0 / 0.25 = 8.0 kW, NOT 2.0 / 4.0 = 0.5 kW
    assert c.target_safe_power_kw == 8.0

# 14. effective max respects EV and station maximum
def test_effective_max_respects_limits(base_state):
    ev1 = base_state.evs[0]
    ev1.max_charging_rate_kw = 11.0
    station = base_state.stations[0]
    station.max_charging_rate_kw = 7.4
    
    weights = priority.WeightConfig()
    candidates = priority.identify_candidates(base_state, weights)
    c = candidates[0]
    
    assert c.effective_max_kw == 7.4

# 15. valid minimum respects EV and station minimum
def test_valid_minimum_respects_limits(base_state):
    ev1 = base_state.evs[0]
    ev1.min_charging_rate_kw = 5.0
    station = base_state.stations[0]
    station.min_charging_rate_kw = 1.0
    
    weights = priority.WeightConfig()
    candidates = priority.identify_candidates(base_state, weights)
    c = candidates[0]
    
    assert c.valid_min_kw == 5.0

def test_invalid_min_max_excludes_candidate(base_state):
    ev1 = base_state.evs[0]
    ev1.min_charging_rate_kw = 11.0
    station = base_state.stations[0]
    station.max_charging_rate_kw = 7.4
    
    # valid_min = 11.0, effective_max = 7.4. valid_min > effective_max
    weights = priority.WeightConfig()
    candidates = priority.identify_candidates(base_state, weights)
    
    # Excluded because unable to receive a valid charging rate
    assert len(candidates) == 0
