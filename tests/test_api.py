import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_state_manager
import json

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_state():
    # Reset state manager before each test to guarantee deterministic isolation
    manager = get_state_manager()
    manager.reset_state()
    yield

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_state_endpoint_structure():
    response = client.get("/api/state")
    assert response.status_code == 200
    data = response.json()
    # verify all canonical top-level sections
    for key in ["simulation", "environment", "grid", "building", "solar", 
                "stations", "evs", "allocations", "alerts", "strategy", "emergency"]:
        assert key in data

def test_simulation_start():
    response = client.post("/api/simulation/start")
    assert response.status_code == 200
    assert response.json()["simulation"]["is_running"] is True

def test_simulation_pause():
    client.post("/api/simulation/start")
    response = client.post("/api/simulation/pause")
    assert response.status_code == 200
    assert response.json()["simulation"]["is_running"] is False

def test_simulation_reset():
    client.post("/api/control/weather", json={"weather": "Rainy"})
    response = client.post("/api/simulation/reset")
    assert response.status_code == 200
    assert response.json()["environment"]["weather"] == "Sunny"

def test_building_demand_validation():
    # Provide enough grid limit so the demand doesn't trip safety invariants
    client.post("/api/control/grid-limit", json={"limit": 50.0})
    
    req = {"ac": 10.0, "lights": 5.0, "lifts": 2.0, "appliances": 3.0}
    response = client.post("/api/control/building-demand", json=req)
    assert response.status_code == 200
    bld = response.json()["building"]
    assert bld["ac_demand"] == 10.0
    assert bld["total_building_demand"] == 20.0
    
    req["ac"] = -5.0
    err_response = client.post("/api/control/building-demand", json=req)
    assert err_response.status_code == 422 # FastAPI Pydantic validation error

def test_grid_limit_validation():
    response = client.post("/api/control/grid-limit", json={"limit": 500.0})
    assert response.status_code == 200
    assert response.json()["grid"]["configured_limit"] == 500.0
    
    err_response = client.post("/api/control/grid-limit", json={"limit": -10.0})
    assert err_response.status_code == 422

def test_weather_validation():
    response = client.post("/api/control/weather", json={"weather": "Cloudy"})
    assert response.status_code == 200
    assert response.json()["environment"]["weather"] == "Cloudy"

def test_spawn_ev_validation():
    ev_req = {
        "ev_id": "EV-1",
        "vehicle_type": "Car",
        "battery_capacity": 50.0,
        "target_soc": 80.0,
        "requested_travel_distance": 100.0,
        "arrival": 0.0,
        "departure": 10.0,
        "minimum_rate": 0.0,
        "maximum_rate": 11.0,
        "station_id": None
    }
    response = client.post("/api/control/spawn-ev", json=ev_req)
    assert response.status_code == 200
    evs = response.json()["evs"]
    assert len(evs) == 1
    assert evs[0]["ev_id"] == "EV-1"
    assert evs[0]["urgency"] == "NORMAL"
    
    invalid_req = ev_req.copy()
    invalid_req["ev_id"] = "EV-2"
    invalid_req["arrival"] = 20.0
    err_response = client.post("/api/control/spawn-ev", json=invalid_req)
    assert err_response.status_code == 422
    
    err_response2 = client.post("/api/control/spawn-ev", json=ev_req)
    assert err_response2.status_code == 400

def test_spawn_urgent_ev_validation():
    ev_req = {
        "ev_id": "EV-U1",
        "vehicle_type": "Car",
        "battery_capacity": 50.0,
        "target_soc": 80.0,
        "requested_travel_distance": 100.0,
        "arrival": 0.0,
        "departure": 10.0,
        "minimum_rate": 0.0,
        "maximum_rate": 11.0,
        "station_id": None,
        "urgency": "URGENT"
    }
    response = client.post("/api/control/spawn-urgent-ev", json=ev_req)
    assert response.status_code == 200
    evs = response.json()["evs"]
    assert len(evs) == 1
    assert evs[0]["urgency"] == "URGENT"

def test_strategy_validation():
    response = client.post("/api/control/strategy", json={"active_strategy": "SOLAR_FIRST"})
    assert response.status_code == 200
    assert response.json()["strategy"]["active_strategy"] == "SOLAR_FIRST"
    
    err_response = client.post("/api/control/strategy", json={"active_strategy": "INVALID"})
    assert err_response.status_code == 422

def test_emergency_endpoints():
    client.post("/api/control/grid-limit", json={"limit": 500.0})
    
    response = client.post("/api/control/emergency/activate")
    assert response.status_code == 200
    state = response.json()
    assert state["emergency"]["emergency_active_state"] is True
    assert state["grid"]["active_limit"] == state["emergency"]["emergency_limit"]
    assert state["grid"]["configured_limit"] == 500.0
    
    response2 = client.post("/api/control/emergency/restore")
    assert response2.status_code == 200
    state2 = response2.json()
    assert state2["emergency"]["emergency_active_state"] is False
    assert state2["grid"]["active_limit"] == 500.0

def test_contract_consistency():
    manager = get_state_manager()
    internal_state_dict = manager.get_state().model_dump(mode='json')
    
    api_response = client.get("/api/state")
    api_state_dict = api_response.json()
    
    assert internal_state_dict == api_state_dict

def test_state_remains_unchanged_after_rejected_mutation():
    response_before = client.get("/api/state")
    state_before = response_before.json()
    
    err_response = client.post("/api/control/grid-limit", json={"limit": -100.0})
    assert err_response.status_code == 422
    
    response_after = client.get("/api/state")
    state_after = response_after.json()
    
    assert state_before == state_after
