import pytest
from pydantic import ValidationError
from app.models.pydantic_state import (
    SystemState, Simulation, Environment, Grid, Building, Solar,
    Station, EV, Allocation, Alert, Strategy, Emergency,
    AlertCategory, StrategyType
)

def test_valid_system_state_construction():
    grid = Grid(configured_limit=100.0, active_limit=100.0)
    emergency = Emergency(emergency_limit=50.0)
    state = SystemState(grid=grid, emergency=emergency)
    
    assert state.grid.configured_limit == 100.0
    assert state.emergency.emergency_limit == 50.0
    assert state.simulation.is_running is False
    assert state.strategy.active_strategy == StrategyType.DEADLINE_FIRST

def test_empty_system_state_construction_fails_without_required():
    # Grid and Emergency are required to have explicit configuration bounds
    with pytest.raises(ValidationError):
        SystemState()

def test_valid_ev_construction():
    ev = EV(
        ev_id="ev_1",
        vehicle_type="Car",
        battery_capacity=50.0,
        current_soc=20.0,
        target_soc=80.0,
        arrival=0.0,
        departure=10.0,
        maximum_rate=11.0
    )
    assert ev.ev_id == "ev_1"
    assert ev.battery_capacity == 50.0

def test_invalid_soc_rejected():
    with pytest.raises(ValidationError):
        EV(
            ev_id="ev_1", vehicle_type="Car", battery_capacity=50.0,
            current_soc=120.0, target_soc=80.0, arrival=0, departure=10, maximum_rate=11.0
        )
    with pytest.raises(ValidationError):
        EV(
            ev_id="ev_1", vehicle_type="Car", battery_capacity=50.0,
            current_soc=-5.0, target_soc=80.0, arrival=0, departure=10, maximum_rate=11.0
        )

def test_invalid_target_soc_rejected():
    with pytest.raises(ValidationError):
        EV(
            ev_id="ev_1", vehicle_type="Car", battery_capacity=50.0,
            current_soc=20.0, target_soc=105.0, arrival=0, departure=10, maximum_rate=11.0
        )

def test_negative_charging_rate_rejected():
    with pytest.raises(ValidationError):
        EV(
            ev_id="ev_1", vehicle_type="Car", battery_capacity=50.0,
            current_soc=20.0, target_soc=80.0, arrival=0, departure=10, 
            maximum_rate=11.0, current_rate=-1.0
        )

def test_minimum_rate_greater_than_maximum_rate_rejected():
    with pytest.raises(ValidationError):
        EV(
            ev_id="ev_1", vehicle_type="Car", battery_capacity=50.0,
            current_soc=20.0, target_soc=80.0, arrival=0, departure=10, 
            minimum_rate=15.0, maximum_rate=11.0
        )

def test_invalid_battery_capacity_rejected():
    with pytest.raises(ValidationError):
        EV(
            ev_id="ev_1", vehicle_type="Car", battery_capacity=-50.0,
            current_soc=20.0, target_soc=80.0, arrival=0, departure=10, maximum_rate=11.0
        )
    with pytest.raises(ValidationError):
        EV(
            ev_id="ev_1", vehicle_type="Car", battery_capacity=0.0,
            current_soc=20.0, target_soc=80.0, arrival=0, departure=10, maximum_rate=11.0
        )

def test_invalid_strategy_rejected():
    with pytest.raises(ValidationError):
        Strategy(active_strategy="INVALID_STRATEGY")

def test_invalid_alert_category_rejected():
    with pytest.raises(ValidationError):
        Alert(
            alert_id="a1", type="NOT_A_CATEGORY", message="test", 
            timestamp=1.0, severity="high"
        )

def test_serialization_to_json():
    grid = Grid(configured_limit=100.0, active_limit=100.0)
    emergency = Emergency(emergency_limit=50.0)
    state = SystemState(grid=grid, emergency=emergency)
    
    ev = EV(
        ev_id="ev_1", vehicle_type="Car", battery_capacity=50.0,
        current_soc=20.0, target_soc=80.0, arrival=0, departure=10, maximum_rate=11.0
    )
    state.evs.append(ev)
    
    alert = Alert(
        alert_id="alert1", type=AlertCategory.SAFETY_EVENT, message="Warn", 
        timestamp=100.0, severity="High"
    )
    state.alerts.append(alert)
    
    json_data = state.model_dump_json()
    assert "ev_1" in json_data
    assert "SAFETY_EVENT" in json_data
    assert "DEADLINE_FIRST" in json_data

def test_nested_ev_station_allocation_state():
    grid = Grid(configured_limit=100.0, active_limit=100.0)
    emergency = Emergency(emergency_limit=50.0)
    state = SystemState(grid=grid, emergency=emergency)
    
    station = Station(station_id="s1", capacity=22.0, maximum_charging_rate=22.0)
    state.stations.append(station)
    
    ev = EV(
        ev_id="ev_1", vehicle_type="Car", battery_capacity=50.0,
        current_soc=20.0, target_soc=80.0, arrival=0, departure=10, maximum_rate=11.0,
        station_id="s1"
    )
    state.evs.append(ev)
    
    alloc = Allocation(ev_id="ev_1", allocated_rate=11.0)
    state.allocations.append(alloc)
    
    assert len(state.evs) == 1
    assert state.evs[0].station_id == "s1"
    assert state.allocations[0].allocated_rate == 11.0

def test_emergency_state_construction():
    emergency = Emergency(emergency_active_state=True, emergency_limit=40.0)
    assert emergency.emergency_active_state is True
    assert emergency.emergency_limit == 40.0
