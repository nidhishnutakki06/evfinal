import pytest
from app.services.validation import StateValidator
from app.models.pydantic_state import SystemState, Grid, Emergency, Building, Solar, Station, EV, Allocation, Simulation

@pytest.fixture
def base_valid_state():
    return SystemState(
        grid=Grid(configured_limit=100.0, active_limit=100.0, grid_import=20.0, available_capacity=40.0),
        emergency=Emergency(emergency_limit=50.0),
        building=Building(ac_demand=10.0, lights_demand=10.0, lifts_demand=10.0, appliances_demand=10.0, total_building_demand=40.0),
        solar=Solar(generation=20.0, usable_solar=20.0, excess_solar=0.0)
    )

def test_validation_1_valid_state_accepted(base_valid_state):
    validator = StateValidator()
    result = validator.validate(base_valid_state)
    assert result.is_valid is True

def test_validation_2_grid_import_above_active_limit_rejected(base_valid_state):
    validator = StateValidator()
    base_valid_state.grid.grid_import = 110.0
    result = validator.validate(base_valid_state)
    assert result.is_valid is False
    assert any("Grid import exceeds active limit" in e for e in result.errors)

def test_validation_3_negative_grid_import_rejected(base_valid_state):
    validator = StateValidator()
    base_valid_state.grid.grid_import = -5.0
    result = validator.validate(base_valid_state)
    assert result.is_valid is False
    assert any("Grid import cannot be negative" in e for e in result.errors)

def test_validation_4_negative_solar_rejected(base_valid_state):
    validator = StateValidator()
    base_valid_state.solar.generation = -10.0
    result = validator.validate(base_valid_state)
    assert result.is_valid is False
    assert any("Solar generation cannot be negative" in e for e in result.errors)

def test_validation_5_invalid_usable_solar_rejected(base_valid_state):
    validator = StateValidator()
    base_valid_state.solar.usable_solar = 30.0 # Generation is 20.0
    result = validator.validate(base_valid_state)
    assert result.is_valid is False
    assert any("Usable solar cannot exceed generation" in e for e in result.errors)

def test_validation_6_invalid_excess_solar_rejected(base_valid_state):
    validator = StateValidator()
    base_valid_state.solar.excess_solar = -1.0
    result = validator.validate(base_valid_state)
    assert result.is_valid is False
    assert any("Excess solar cannot be negative" in e for e in result.errors)
    
def test_validation_7_invalid_building_demand_rejected(base_valid_state):
    validator = StateValidator()
    base_valid_state.building.ac_demand = -5.0
    result = validator.validate(base_valid_state)
    assert result.is_valid is False
    assert any("Building component demands cannot be negative" in e for e in result.errors)

def test_validation_8_ev_rate_above_ev_maximum_rejected(base_valid_state):
    validator = StateValidator()
    ev = EV(ev_id="E1", vehicle_type="Car", battery_capacity=50, target_soc=100, arrival=0, departure=10, maximum_rate=11.0, current_rate=22.0, current_soc=50)
    base_valid_state.evs.append(ev)
    result = validator.validate(base_valid_state)
    assert result.is_valid is False
    assert any("current rate exceeds EV max rate" in e for e in result.errors)

def test_validation_9_ev_rate_above_station_maximum_rejected(base_valid_state):
    validator = StateValidator()
    ev = EV(ev_id="E1", vehicle_type="Car", battery_capacity=50, target_soc=100, arrival=0, departure=10, maximum_rate=50.0, current_rate=22.0, current_soc=50, station_id="S1")
    st = Station(station_id="S1", capacity=11.0, maximum_charging_rate=11.0, occupancy=True, connected_ev_id="E1")
    base_valid_state.evs.append(ev)
    base_valid_state.stations.append(st)
    result = validator.validate(base_valid_state)
    assert result.is_valid is False
    assert any("current rate exceeds station S1 max rate" in e for e in result.errors)

def test_validation_10_invalid_soc_rejected(base_valid_state):
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        EV(ev_id="E1", vehicle_type="Car", battery_capacity=50, target_soc=100, arrival=0, departure=10, maximum_rate=11.0, current_soc=105.0)

def test_validation_11_invalid_target_soc_rejected(base_valid_state):
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        EV(ev_id="E1", vehicle_type="Car", battery_capacity=50, target_soc=105.0, arrival=0, departure=10, maximum_rate=11.0, current_soc=50.0)

def test_validation_12_departed_ev_charging_rejected(base_valid_state):
    validator = StateValidator()
    base_valid_state.simulation.simulation_time = 15.0
    ev = EV(ev_id="E1", vehicle_type="Car", battery_capacity=50, target_soc=100.0, arrival=0, departure=10.0, maximum_rate=11.0, current_soc=50.0, current_rate=5.0)
    base_valid_state.evs.append(ev)
    result = validator.validate(base_valid_state)
    assert result.is_valid is False
    assert any("has departed but still has a charging rate" in e for e in result.errors)

def test_validation_13_target_reached_ev_charging_rejected(base_valid_state):
    validator = StateValidator()
    ev = EV(ev_id="E1", vehicle_type="Car", battery_capacity=50, target_soc=80.0, arrival=0, departure=10.0, maximum_rate=11.0, current_soc=85.0, current_rate=5.0)
    base_valid_state.evs.append(ev)
    result = validator.validate(base_valid_state)
    assert result.is_valid is False
    assert any("reached target SOC but still has a charging rate" in e for e in result.errors)

def test_validation_14_station_ev_reference_inconsistency_rejected(base_valid_state):
    validator = StateValidator()
    ev = EV(ev_id="E1", vehicle_type="Car", battery_capacity=50, target_soc=80.0, arrival=0, departure=10.0, maximum_rate=11.0, current_soc=50.0, station_id="S1")
    st = Station(station_id="S1", capacity=11.0, maximum_charging_rate=11.0, occupancy=True, connected_ev_id="E2")
    base_valid_state.evs.append(ev)
    base_valid_state.stations.append(st)
    result = validator.validate(base_valid_state)
    assert result.is_valid is False
    assert any("station references E2" in e for e in result.errors)

def test_validation_15_invalid_station_allocation_rejected(base_valid_state):
    validator = StateValidator()
    st = Station(station_id="S1", capacity=11.0, maximum_charging_rate=11.0, allocated_power=22.0)
    base_valid_state.stations.append(st)
    result = validator.validate(base_valid_state)
    assert result.is_valid is False
    assert any("allocated power exceeds maximum charging rate" in e for e in result.errors)

def test_validation_16_emergency_limit_inconsistency_rejected(base_valid_state):
    validator = StateValidator()
    base_valid_state.emergency.emergency_active_state = True
    base_valid_state.grid.active_limit = 100.0 # Should be 50.0
    result = validator.validate(base_valid_state)
    assert result.is_valid is False
    assert any("Active grid limit must match emergency limit when emergency is active" in e for e in result.errors)

def test_validation_17_validator_does_not_mutate_candidate(base_valid_state):
    validator = StateValidator()
    original_dump = base_valid_state.model_dump()
    validator.validate(base_valid_state)
    assert base_valid_state.model_dump() == original_dump
    
    # Test with invalid state
    base_valid_state.grid.grid_import = 999.0
    original_dump_invalid = base_valid_state.model_dump()
    validator.validate(base_valid_state)
    assert base_valid_state.model_dump() == original_dump_invalid
