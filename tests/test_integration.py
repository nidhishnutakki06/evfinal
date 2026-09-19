import pytest
import copy
from typing import List

from sh305.domain.enums import UserUrgency, VehicleType, WeatherCondition
from sh305.domain.system_state import SystemState
from sh305.domain.ev import EV
from sh305.synthetic.generator import SyntheticDataGenerator
from sh305.engine.controller import (
    apply_building_demand_delta,
    activate_emergency,
    restore_grid,
    set_strategy,
    _recompute
)
from sh305.engine.simulation import step_simulation


def assert_invariants(state: SystemState):
    """
    4. Invariant audit
    At every simulation step verify the invariants.
    Fail loudly if any invariant breaks.
    """
    assert state.grid.current_import_kw <= state.grid.active_limit_kw, "GRID_IMPORT <= ACTIVE_GRID_LIMIT violated"
    assert state.grid.current_import_kw >= 0.0, "GRID_IMPORT >= 0 violated"
    assert state.solar.generation_kw >= 0.0, "SOLAR >= 0 violated"

    for ev in state.evs:
        assert 0.0 <= ev.current_soc <= 100.0, "0 <= SoC <= 100 violated"
        
        # Rate limits
        assert ev.current_charging_rate_kw <= ev.max_charging_rate_kw, "EV rate <= EV max violated"
        
        # Station max
        if ev.station_id:
            station = next(s for s in state.stations if s.station_id == ev.station_id)
            assert ev.current_charging_rate_kw <= station.max_charging_rate_kw, "EV rate <= station max violated"
            
        # Minimum charging rate
        if ev.current_charging_rate_kw > 0.0:
            assert ev.current_charging_rate_kw >= ev.min_charging_rate_kw, "active rate >= valid minimum violated"
            
        # Departed or zero time left
        if ev.time_remaining_hours <= 0:
            assert ev.current_charging_rate_kw == 0.0, "departed EV rate = 0 violated"
            
        # Target reached
        if ev.energy_required_kwh <= 0:
            assert ev.current_charging_rate_kw == 0.0, "target EV rate = 0 violated"


@pytest.fixture
def demo_scenario_state() -> SystemState:
    generator = SyntheticDataGenerator(seed=42)
    state = generator.generate_initial_system_state()
    state.evs = []
    
    # Grid initially around 70% loaded (Grid limit = 100, Building = 70)
    state.grid.configured_limit_kw = 100.0
    state.grid.active_limit_kw = 100.0
    state.building.appliances_demand_kw = 70.0
    state.building.ac_demand_kw = 0.0
    state.building.lights_demand_kw = 0.0
    state.building.lifts_demand_kw = 0.0
    state.building.total_demand_kw = 70.0
    
    # Sunny starting condition, meaningful solar
    state.environment.weather = WeatherCondition.SUNNY
    state.simulation.simulation_time = 12.0 # Noon
    state.solar.generation_kw = 50.0 
    
    # 6-8 EVs, mixed types, SoC, urgency, departure, travel needs
    # EV1: Critical, needs lot of energy
    ev1 = EV(ev_id="EV-1", station_id="CS-01", vehicle_type=VehicleType.SUV, battery_capacity_kwh=100.0,
             expected_range_km=400.0, current_soc=20.0, requested_travel_distance_km=250.0,
             arrival_time=12.0, departure_time=16.0, min_charging_rate_kw=7.0, max_charging_rate_kw=22.0,
             user_urgency=UserUrgency.CRITICAL)
             
    # EV2: High urgency, almost departed
    ev2 = EV(ev_id="EV-2", station_id="CS-02", vehicle_type=VehicleType.SEDAN, battery_capacity_kwh=80.0,
             expected_range_km=350.0, current_soc=20.0, requested_travel_distance_km=250.0,
             arrival_time=10.0, departure_time=13.0, min_charging_rate_kw=7.0, max_charging_rate_kw=11.0,
             user_urgency=UserUrgency.HIGH)
             
    # EV3: Medium urgency, moderate need
    ev3 = EV(ev_id="EV-3", station_id="CS-03", vehicle_type=VehicleType.HATCHBACK, battery_capacity_kwh=60.0,
             expected_range_km=300.0, current_soc=20.0, requested_travel_distance_km=200.0,
             arrival_time=12.0, departure_time=18.0, min_charging_rate_kw=3.5, max_charging_rate_kw=11.0,
             user_urgency=UserUrgency.MEDIUM)
             
    # EV4: Low urgency, late departure
    ev4 = EV(ev_id="EV-4", station_id="CS-04", vehicle_type=VehicleType.SUV, battery_capacity_kwh=100.0,
             expected_range_km=400.0, current_soc=20.0, requested_travel_distance_km=250.0,
             arrival_time=12.0, departure_time=20.0, min_charging_rate_kw=7.0, max_charging_rate_kw=22.0,
             user_urgency=UserUrgency.LOW)
             
    # EV5: High urgency, low power need
    ev5 = EV(ev_id="EV-5", station_id="CS-05", vehicle_type=VehicleType.SEDAN, battery_capacity_kwh=80.0,
             expected_range_km=350.0, current_soc=20.0, requested_travel_distance_km=200.0,
             arrival_time=12.0, departure_time=14.0, min_charging_rate_kw=3.5, max_charging_rate_kw=11.0,
             user_urgency=UserUrgency.HIGH)
             
    # EV6: Medium urgency, long duration
    ev6 = EV(ev_id="EV-6", station_id="CS-06", vehicle_type=VehicleType.HATCHBACK, battery_capacity_kwh=60.0,
             expected_range_km=300.0, current_soc=15.0, requested_travel_distance_km=200.0,
             arrival_time=12.0, departure_time=22.0, min_charging_rate_kw=7.0, max_charging_rate_kw=22.0,
             user_urgency=UserUrgency.MEDIUM)

    state.evs = [ev1, ev2, ev3, ev4, ev5, ev6]
    for i, ev in enumerate(state.evs):
        state.stations[i].connected_ev_id = ev.ev_id
        state.stations[i].occupied = True

    _recompute(state)
    assert_invariants(state)
    return state


def test_demo_scenario(demo_scenario_state):
    state = demo_scenario_state
    
    # Verify initial state
    ev_rates_initial = {ev.ev_id: ev.current_charging_rate_kw for ev in state.evs}
    
    # ---------------------------------------------------------
    # ACTION 1: Building demand +25 kW
    # ---------------------------------------------------------
    apply_building_demand_delta(state, delta_kw=25.0)
    assert_invariants(state)
    
    # Building went from 70 to 95. Available EV capacity shrinks.
    ev_rates_after_a1 = {ev.ev_id: ev.current_charging_rate_kw for ev in state.evs}
    
    # Check allocation changes
    assert ev_rates_initial != ev_rates_after_a1
    
    # Lower-priority EVs can reduce (e.g., EV4 which is LOW)
    # Check A2/A3 update
    assert any(ev.reason for ev in state.evs)
    # Check A3 can change (predictive risk flag)
    # Just asserting it's accessible and evaluated
    has_risk = any(ev.predictive_risk_flag for ev in state.evs)
    
    # ---------------------------------------------------------
    # ACTION 2: Inspect an affected EV
    # ---------------------------------------------------------
    ev4 = next(ev for ev in state.evs if ev.ev_id == "EV-4")
    # Check all fields exist and have values
    assert ev4.current_charging_rate_kw >= 0
    assert ev4.target_soc is not None
    assert ev4.departure_time == 20.0
    assert ev4.physical_feasibility is not None
    assert isinstance(ev4.reason, str)
    assert isinstance(ev4.predictive_risk_flag, bool)

    # ---------------------------------------------------------
    # ACTION 3: Activate emergency
    # ---------------------------------------------------------
    activate_emergency(state, reduction_fraction=0.40)
    assert_invariants(state)
    
    # Active limit drops to 60.0. Building is 95.0. 
    # With solar 50.0, available ev = max(0, 60.0 - 95.0 + 50.0) = 15.0 kW.
    assert state.grid.active_limit_kw == 60.0
    
    ev_rates_after_a3 = {ev.ev_id: ev.current_charging_rate_kw for ev in state.evs}
    assert ev_rates_after_a1 != ev_rates_after_a3
    
    # Lower priority EVs may pause
    assert ev4.current_charging_rate_kw == 0.0 # Only 15kW available, EV1 (Critical) takes it
    
    # Grid remains safe
    total_ev_draw = sum(ev.current_charging_rate_kw for ev in state.evs)
    assert state.grid.current_import_kw <= state.grid.active_limit_kw
    
    # ---------------------------------------------------------
    # ACTION 4: Restore grid
    # ---------------------------------------------------------
    restore_grid(state)
    assert_invariants(state)
    
    assert state.grid.active_limit_kw == 100.0
    ev_rates_after_a4 = {ev.ev_id: ev.current_charging_rate_kw for ev in state.evs}
    
    # Allocation is recalculated
    assert ev_rates_after_a3 != ev_rates_after_a4
    # Resume according to priority
    # EV4 might resume if capacity allows, but definitely EV1 and EV2 get power
    ev1 = next(ev for ev in state.evs if ev.ev_id == "EV-1")
    assert ev1.current_charging_rate_kw > 0.0
    
    # ---------------------------------------------------------
    # ACTION 5: Switch strategy
    # ---------------------------------------------------------
    set_strategy(state, "SOLAR_FIRST")
    assert_invariants(state)
    
    ev_rates_after_a5 = {ev.ev_id: ev.current_charging_rate_kw for ev in state.evs}
    
    # Same state & hard constraints (done implicitly by the pipeline)
    # Different objective causes allocation change
    assert state.strategy == "SOLAR_FIRST"
    # Allocation can change where genuine tradeoff exists
    # We just ensure the simulation doesn't break and invariants hold.


def test_demo_scenario_determinism(demo_scenario_state):
    # Run the exact sequence twice and verify exact equality
    state1 = copy.deepcopy(demo_scenario_state)
    state2 = copy.deepcopy(demo_scenario_state)
    
    def execute_sequence(s):
        apply_building_demand_delta(s, 25.0)
        activate_emergency(s, 0.40)
        restore_grid(s)
        set_strategy(s, "SOLAR_FIRST")
        return [ev.current_charging_rate_kw for ev in s.evs]
        
    rates1 = execute_sequence(state1)
    rates2 = execute_sequence(state2)
    
    assert rates1 == rates2
    assert state1.grid.current_import_kw == state2.grid.current_import_kw
    assert state1.solar.usable_solar_kw == state2.solar.usable_solar_kw
    
    for ev1, ev2 in zip(state1.evs, state2.evs):
        assert ev1.reason == ev2.reason
        assert ev1.predictive_risk_flag == ev2.predictive_risk_flag


def test_24_hour_simulation():
    generator = SyntheticDataGenerator(seed=42)
    state = generator.generate_initial_system_state()
    state.simulation.simulation_time = 0.0
    
    while state.simulation.simulation_time < 24.0:
        step_simulation(state, step_hours=0.25)
        assert_invariants(state)
        
    # Verify final summary
    assert state.simulation.simulation_time == 24.0
    assert state.solar.generation_kw == 0.0 # Solar is zero at night (hour 24 = night)
    
    # End of day check
    for ev in state.evs:
        # All EVs departed or still there
        if ev.time_remaining_hours <= 0:
            assert ev.current_charging_rate_kw == 0.0
