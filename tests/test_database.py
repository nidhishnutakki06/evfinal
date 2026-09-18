import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.models.sqlalchemy_db import Base, EVDefinition, StationDefinition, ScenarioProfile
from app.services.repository import PersistenceRepository

# In-memory database for isolated testing, ensuring it never hits development DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def repo(db_session):
    return PersistenceRepository(db_session)

def test_engine_and_session_creation(db_session):
    # Simply having the fixture yield without error proves engine and session work.
    assert db_session is not None

def test_create_and_read_ev_definition(repo):
    ev_data = {
        "id": "EV-TEST-1",
        "vehicle_type": "Car",
        "battery_capacity": 60.0,
        "range": 350.0,
        "maximum_charging_rate": 11.0
    }
    created_ev = repo.create_ev_definition(ev_data)
    assert created_ev.id == "EV-TEST-1"
    assert created_ev.battery_capacity == 60.0

    retrieved_ev = repo.get_ev_definition("EV-TEST-1")
    assert retrieved_ev is not None
    assert retrieved_ev.vehicle_type == "Car"

def test_update_ev_definition(repo):
    ev_data = {
        "id": "EV-TEST-2",
        "vehicle_type": "Car",
        "battery_capacity": 60.0,
        "maximum_charging_rate": 11.0
    }
    repo.create_ev_definition(ev_data)
    
    updated_ev = repo.update_ev_definition("EV-TEST-2", {"battery_capacity": 70.0})
    assert updated_ev.battery_capacity == 70.0

    retrieved_ev = repo.get_ev_definition("EV-TEST-2")
    assert retrieved_ev.battery_capacity == 70.0

def test_create_and_read_station_definition(repo):
    station_data = {
        "station_id": "ST-TEST-1",
        "capacity": 22.0,
        "maximum_charging_rate": 22.0
    }
    created_st = repo.create_station_definition(station_data)
    assert created_st.station_id == "ST-TEST-1"
    
    retrieved_st = repo.get_station_definition("ST-TEST-1")
    assert retrieved_st is not None
    assert retrieved_st.capacity == 22.0

def test_create_and_read_scenario_profile(repo):
    profile_data = {
        "id": "SC-TEST-1",
        "name": "Test Scenario",
        "scenario_data": {"building": "data"}
    }
    created_sc = repo.create_scenario_profile(profile_data)
    assert created_sc.name == "Test Scenario"
    
    retrieved_sc = repo.get_scenario_profile("SC-TEST-1")
    assert retrieved_sc is not None
    assert retrieved_sc.scenario_data == {"building": "data"}

def test_uniqueness_constraints(db_session, repo):
    ev_data = {
        "id": "EV-DUP",
        "vehicle_type": "Car",
        "battery_capacity": 60.0,
        "maximum_charging_rate": 11.0
    }
    repo.create_ev_definition(ev_data)
    
    with pytest.raises(IntegrityError):
        # Attempting to insert duplicate ID
        ev2 = EVDefinition(
            id="EV-DUP", vehicle_type="Truck", battery_capacity=100.0, maximum_charging_rate=50.0
        )
        db_session.add(ev2)
        db_session.commit()
    db_session.rollback()

def test_invalid_structural_values_rejected(db_session):
    with pytest.raises(IntegrityError):
        # Negative battery capacity violates check constraint
        ev = EVDefinition(
            id="EV-INV", vehicle_type="Car", battery_capacity=-10.0, maximum_charging_rate=11.0
        )
        db_session.add(ev)
        db_session.commit()
    db_session.rollback()
    
    with pytest.raises(IntegrityError):
        # Max rate < min rate violates check constraint
        ev = EVDefinition(
            id="EV-INV2", vehicle_type="Car", battery_capacity=50.0, minimum_charging_rate=22.0, maximum_charging_rate=11.0
        )
        db_session.add(ev)
        db_session.commit()
    db_session.rollback()

def test_rollback_error_behavior(db_session, repo):
    ev_data = {
        "id": "EV-SAFE",
        "vehicle_type": "Car",
        "battery_capacity": 60.0,
        "maximum_charging_rate": 11.0
    }
    repo.create_ev_definition(ev_data)
    
    try:
        ev2 = EVDefinition(
            id="EV-SAFE", vehicle_type="Truck", battery_capacity=-10.0, maximum_charging_rate=50.0
        )
        db_session.add(ev2)
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
        
    # Ensure original EV-SAFE is still there and session is functional
    retrieved = repo.get_ev_definition("EV-SAFE")
    assert retrieved is not None
    assert retrieved.vehicle_type == "Car"
