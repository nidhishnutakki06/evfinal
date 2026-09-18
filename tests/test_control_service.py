import pytest
from app.services.state_manager import RuntimeStateManager
from app.core.engine_boundary import EngineBoundary
from app.services.validation import StateValidator
from app.services.control import ControlService

@pytest.fixture
def control_service():
    state_manager = RuntimeStateManager()
    engine = EngineBoundary()
    validator = StateValidator()
    return ControlService(state_manager, engine, validator)

def test_control_service_orchestration_flow(control_service):
    # Tests that inputs correctly invoke deep copy, context calculation, and valid state replacement
    
    # Process valid change
    new_state = control_service.process_grid_limit(limit=250.0)
    assert new_state.grid.configured_limit == 250.0
    
    # State manager should reflect the replaced canonical state
    assert control_service.state_manager.get_state().grid.configured_limit == 250.0

def test_control_service_rejects_invalid_candidate(control_service):
    # Initialize valid state
    control_service.process_grid_limit(limit=100.0)
    canonical = control_service.state_manager.get_state()
    assert canonical.grid.configured_limit == 100.0
    assert canonical.grid.active_limit == 100.0
    
    # To test invariant rejection, we bypass normal inputs and inject a bad state
    # Wait, the validation logic rejects grid_import > active_limit.
    # Currently grid_import is 0.0.
    # Let's mock the validator to reject the candidate to prove rejection flow.
    class MockValidator(StateValidator):
        def validate(self, candidate):
            from app.services.validation import ValidationResult
            return ValidationResult(is_valid=False, errors=["Mock rejection"])
            
    control_service.validator = MockValidator()
    
    with pytest.raises(ValueError, match="Candidate state rejected by validation invariants: Mock rejection"):
        control_service.process_grid_limit(limit=200.0)
        
    # Crucial: the canonical state must REMAIN UNCHANGED (100.0)
    assert control_service.state_manager.get_state().grid.configured_limit == 100.0

def test_control_service_reset_simulation(control_service):
    # Set a dirty state
    control_service.process_grid_limit(limit=400.0)
    control_service.process_simulation_status(True)
    control_service.process_emergency_activation(True)
    
    assert control_service.state_manager.get_state().simulation.is_running is True
    assert control_service.state_manager.get_state().emergency.emergency_active_state is True
    
    # Reset
    control_service.process_reset_simulation()
    
    pristine = control_service.state_manager.get_state()
    # Live variables reset
    assert pristine.simulation.is_running is False
    assert pristine.emergency.emergency_active_state is False
    # Static config preserved
    assert pristine.grid.configured_limit == 400.0
    assert pristine.grid.active_limit == 400.0

def test_control_service_spawn_ev_station_assignment(control_service):
    # Create station first
    from app.models.pydantic_state import Station
    candidate = control_service.state_manager.get_state()
    candidate.stations.append(Station(
        station_id="ST-100",
        capacity=22.0,
        minimum_charging_rate=0.0,
        maximum_charging_rate=22.0,
        occupancy=False,
        status="AVAILABLE"
    ))
    control_service.state_manager.replace_state(candidate)
    
    ev_data = {
        "ev_id": "EV-X",
        "vehicle_type": "Car",
        "battery_capacity": 50.0,
        "target_soc": 80.0,
        "arrival": 0.0,
        "departure": 10.0,
        "maximum_rate": 11.0,
        "station_id": "ST-100"
    }
    control_service.process_spawn_ev(ev_data)
    
    state = control_service.state_manager.get_state()
    assert state.evs[0].ev_id == "EV-X"
    assert state.stations[0].occupancy is True
    assert state.stations[0].connected_ev_id == "EV-X"

def test_control_service_spawn_ev_station_occupied(control_service):
    # Setup occupied station
    from app.models.pydantic_state import Station
    candidate = control_service.state_manager.get_state()
    candidate.stations.append(Station(
        station_id="ST-100",
        capacity=22.0,
        minimum_charging_rate=0.0,
        maximum_charging_rate=22.0,
        occupancy=True,
        connected_ev_id="EV-OTHER",
        status="CHARGING"
    ))
    control_service.state_manager.replace_state(candidate)
    
    ev_data = {
        "ev_id": "EV-NEW",
        "vehicle_type": "Car",
        "battery_capacity": 50.0,
        "target_soc": 80.0,
        "arrival": 0.0,
        "departure": 10.0,
        "maximum_rate": 11.0,
        "station_id": "ST-100"
    }
    
    import pytest
    with pytest.raises(ValueError, match="Station is already occupied"):
        control_service.process_spawn_ev(ev_data)

