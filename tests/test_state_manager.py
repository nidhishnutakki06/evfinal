import pytest
from app.services.state_manager import RuntimeStateManager
from app.models.pydantic_state import SystemState, EV, Grid
from app.services.repository import PersistenceRepository
from app.models.sqlalchemy_db import Base, EVDefinition, StationDefinition
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def repo():
    # Independent memory DB
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield PersistenceRepository(db)
    db.close()

def test_initial_state_valid_and_retrieval():
    manager = RuntimeStateManager()
    state = manager.get_state()
    assert isinstance(state, SystemState)
    assert len(state.evs) == 0
    assert len(state.stations) == 0
    assert state.grid.configured_limit == 0.0
    assert state.emergency.emergency_active_state is False

def test_safe_state_access_mutation_protection():
    manager = RuntimeStateManager()
    state = manager.get_state()
    # Mutate the returned copy
    state.grid.configured_limit = 999.0
    # Original should be strictly untouched inside manager
    original_state = manager.get_state()
    assert original_state.grid.configured_limit == 0.0

def test_replace_state_with_valid_state():
    manager = RuntimeStateManager()
    state = manager.get_state()
    state.grid.configured_limit = 50.0
    state.grid.active_limit = 50.0
    
    success = manager.replace_state(state)
    assert success is True
    assert manager.get_state().grid.configured_limit == 50.0

def test_invalid_state_replacement_rejected():
    manager = RuntimeStateManager()
    state = manager.get_state()
    
    # Intentionally violate constraints (negative limit)
    state.grid.configured_limit = -100.0
    
    success = manager.replace_state(state)
    assert success is False
    
    # Previous state preserved
    assert manager.get_state().grid.configured_limit == 0.0

def test_reset_behavior():
    manager = RuntimeStateManager()
    state = manager.get_state()
    state.grid.configured_limit = 100.0
    state.grid.active_limit = 50.0
    manager.replace_state(state)
    
    manager.reset_state()
    reset_state = manager.get_state()
    # Active limit should inherently restore to configured limit after reset
    assert reset_state.grid.configured_limit == 100.0
    assert reset_state.grid.active_limit == 100.0
    assert len(reset_state.evs) == 0

def test_initialize_from_definitions(repo):
    repo.create_ev_definition({
        "id": "EV-1", "vehicle_type": "Car", "battery_capacity": 50.0,
        "range": 200.0, "minimum_charging_rate": 0.0, "maximum_charging_rate": 11.0
    })
    repo.create_station_definition({
        "station_id": "ST-1", "capacity": 22.0, "maximum_charging_rate": 22.0
    })
    
    manager = RuntimeStateManager()
    manager.initialize_from_definitions(repo)
    
    state = manager.get_state()
    assert len(state.evs) == 1
    assert state.evs[0].ev_id == "EV-1"
    assert state.evs[0].battery_capacity == 50.0
    assert state.evs[0].current_soc == 0.0 # Deterministic runtime initialization
    
    assert len(state.stations) == 1
    assert state.stations[0].station_id == "ST-1"
    assert state.stations[0].capacity == 22.0

def test_reset_does_not_delete_database(repo):
    repo.create_ev_definition({
        "id": "EV-1", "vehicle_type": "Car", "battery_capacity": 50.0,
        "range": 200.0, "minimum_charging_rate": 0.0, "maximum_charging_rate": 11.0
    })
    manager = RuntimeStateManager()
    manager.initialize_from_definitions(repo)
    
    manager.reset_state()
    # Live EVs are cleared from runtime
    assert len(manager.get_state().evs) == 0
    # DB remains persistently populated
    assert len(repo.get_all_ev_definitions()) == 1

def test_runtime_boundary_preservation(repo):
    repo.create_ev_definition({
        "id": "EV-1", "vehicle_type": "Car", "battery_capacity": 50.0,
        "maximum_charging_rate": 11.0
    })
    manager = RuntimeStateManager()
    manager.initialize_from_definitions(repo)
    
    # Mutating runtime copy does not change database
    state = manager.get_state()
    state.evs[0].battery_capacity = 999.0
    manager.replace_state(state)
    
    db_ev = repo.get_ev_definition("EV-1")
    assert db_ev.battery_capacity == 50.0 # Strictly unchanged
