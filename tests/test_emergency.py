import pytest
import copy
from sh305.domain.enums import UserUrgency, VehicleType
from sh305.synthetic.generator import SyntheticDataGenerator
from sh305.engine.controller import activate_emergency, restore_grid

@pytest.fixture
def base_state():
    generator = SyntheticDataGenerator(seed=42)
    state = generator.generate_initial_system_state()
    # Clear EVs for a controlled scenario
    state.evs = []
    
    # Grid setup
    state.grid.configured_limit_kw = 50.0
    state.grid.active_limit_kw = 50.0
    
    # Building demand and solar
    state.building.appliances_demand_kw = 10.0
    state.building.total_demand_kw = 10.0
    state.solar.generation_kw = 0.0
    
    # Initial available capacity for EVs = 50 - 10 + 0 = 40.0 kW
    
    # EV1: High priority (CRITICAL urgency)
    from sh305.domain.ev import EV
    ev1 = EV(
        ev_id="EV-1",
        station_id="CS-01",
        vehicle_type=VehicleType.SUV,
        battery_capacity_kwh=100.0,
        expected_range_km=400.0,
        current_soc=20.0,
        requested_travel_distance_km=200.0,
        arrival_time=8.0,
        departure_time=12.0,
        min_charging_rate_kw=7.0,
        max_charging_rate_kw=22.0,
        user_urgency=UserUrgency.CRITICAL
    )
    
    # EV2: Lower priority (LOW urgency)
    ev2 = EV(
        ev_id="EV-2",
        station_id="CS-02",
        vehicle_type=VehicleType.HATCHBACK,
        battery_capacity_kwh=60.0,
        expected_range_km=300.0,
        current_soc=20.0,
        requested_travel_distance_km=150.0,
        arrival_time=8.0,
        departure_time=18.0,
        min_charging_rate_kw=7.0,
        max_charging_rate_kw=11.0,
        user_urgency=UserUrgency.LOW
    )
    
    # EV3: Another low priority EV that will just be slightly lower priority than EV2 or EV1
    ev3 = EV(
        ev_id="EV-3",
        station_id="CS-03",
        vehicle_type=VehicleType.SEDAN,
        battery_capacity_kwh=80.0,
        expected_range_km=350.0,
        current_soc=30.0,
        requested_travel_distance_km=100.0,
        arrival_time=8.0,
        departure_time=20.0,
        min_charging_rate_kw=7.0,
        max_charging_rate_kw=11.0,
        user_urgency=UserUrgency.MEDIUM
    )
    
    state.stations[0].connected_ev_id = "EV-1"
    state.stations[0].occupied = True
    state.stations[1].connected_ev_id = "EV-2"
    state.stations[1].occupied = True
    state.stations[2].connected_ev_id = "EV-3"
    state.stations[2].occupied = True
    
    state.evs = [ev1, ev2, ev3]
    
    # Baseline compute
    from sh305.engine.controller import _recompute
    _recompute(state)
    return state


def test_emergency_reduces_active_limit(base_state):
    assert base_state.grid.active_limit_kw == 50.0
    assert not base_state.emergency
    
    activate_emergency(base_state, reduction_fraction=0.40)
    
    assert base_state.emergency is True
    assert base_state.grid.emergency_mode is True
    # 50.0 * 0.6 = 30.0
    assert base_state.grid.active_limit_kw == 30.0


def test_emergency_pauses_lower_priority_evs_and_prevents_sub_minimum(base_state):
    # Before emergency, available EV capacity = 40.0
    # EV1 wants ~17.5kW (or maxed at 22kW), EV2 wants ~7.5kW, EV3 wants ~3kW.
    # Total required is around 30kW. All can charge safely.
    ev1_initial = base_state.evs[0].current_charging_rate_kw
    ev2_initial = base_state.evs[1].current_charging_rate_kw
    ev3_initial = base_state.evs[2].current_charging_rate_kw
    
    # Ensure they are initially charging at least their minimums
    assert ev1_initial >= 7.0
    assert ev2_initial >= 7.0
    assert ev3_initial >= 7.0
    
    # Trigger emergency (80% reduction -> active limit = 10.0kW)
    # Available for EVs = 10.0 - 10.0 (building) = 0.0 kW
    # Let's do 60% reduction -> active limit = 20.0kW
    # Available for EVs = 20.0 - 10.0 (building) = 10.0 kW
    # EV1 needs at least 7.0. It will get it because it's CRITICAL.
    # The remaining 3.0 kW is not enough for EV2 or EV3's minimum of 7.0.
    # So they should be paused!
    activate_emergency(base_state, reduction_fraction=0.60)
    
    ev1_emg = base_state.evs[0].current_charging_rate_kw
    ev2_emg = base_state.evs[1].current_charging_rate_kw
    ev3_emg = base_state.evs[2].current_charging_rate_kw
    
    # Allocation changed
    assert ev1_emg != ev1_initial or ev2_emg != ev2_initial
    
    # Higher priority preserved (at least its valid min)
    assert ev1_emg >= 7.0
    
    # Lower priorities paused (no sub-minimum charging)
    assert ev2_emg == 0.0
    assert ev3_emg == 0.0
    
    # No grid overload
    total_ev_draw = ev1_emg + ev2_emg + ev3_emg
    assert base_state.building.total_demand_kw + total_ev_draw <= base_state.grid.active_limit_kw


def test_a2_a3_update_after_emergency(base_state):
    activate_emergency(base_state, reduction_fraction=0.60)
    # Explanations (A2) should be updated
    assert len(base_state.evs[1].reason) > 0
    # Predictive risk (A3) should be triggered for paused EVs if they fall behind schedule
    assert any(ev.predictive_risk_flag for ev in base_state.evs)


def test_restore_recalculates_allocation(base_state):
    activate_emergency(base_state, reduction_fraction=0.60)
    assert base_state.evs[1].current_charging_rate_kw == 0.0
    
    restore_grid(base_state)
    
    assert base_state.emergency is False
    assert base_state.grid.emergency_mode is False
    assert base_state.grid.active_limit_kw == 50.0
    
    # They should resume charging based on priority
    assert base_state.evs[1].current_charging_rate_kw >= 7.0
    assert base_state.evs[2].current_charging_rate_kw >= 7.0


def test_paused_evs_do_not_restart_blindly(base_state):
    # What if restoring the grid still doesn't have enough power for everyone?
    # Say we restore, but also building demand spikes up significantly.
    activate_emergency(base_state, reduction_fraction=0.60)
    
    # Before restoring, we increase building demand to 35.0 kW
    # Available for EVs will be 50.0 - 35.0 = 15.0 kW
    # 15.0 is enough for EV1 (>=7.0) and EV2 (>=7.0), but not EV3.
    base_state.building.appliances_demand_kw = 35.0
    base_state.building.total_demand_kw = 35.0
    
    restore_grid(base_state)
    
    ev1_res = base_state.evs[0].current_charging_rate_kw
    ev2_res = base_state.evs[1].current_charging_rate_kw
    ev3_res = base_state.evs[2].current_charging_rate_kw
    
    # EV1 and EV2 might fit, EV3 definitely should be paused to not exceed grid limit
    assert ev1_res >= 7.0
    assert ev2_res >= 0.0 # Might fit
    assert ev3_res == 0.0 # Will not fit along with others
    
    total_ev_draw = ev1_res + ev2_res + ev3_res
    assert base_state.building.total_demand_kw + total_ev_draw <= base_state.grid.active_limit_kw


def test_deterministic_repeated_emergency_restore(base_state):
    state_copy_1 = copy.deepcopy(base_state)
    activate_emergency(state_copy_1, reduction_fraction=0.50)
    rates_emg_1 = [ev.current_charging_rate_kw for ev in state_copy_1.evs]
    restore_grid(state_copy_1)
    rates_res_1 = [ev.current_charging_rate_kw for ev in state_copy_1.evs]
    
    state_copy_2 = copy.deepcopy(base_state)
    activate_emergency(state_copy_2, reduction_fraction=0.50)
    rates_emg_2 = [ev.current_charging_rate_kw for ev in state_copy_2.evs]
    restore_grid(state_copy_2)
    rates_res_2 = [ev.current_charging_rate_kw for ev in state_copy_2.evs]
    
    assert rates_emg_1 == rates_emg_2
    assert rates_res_1 == rates_res_2
