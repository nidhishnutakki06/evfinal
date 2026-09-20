import pytest
from app.services.state_manager import RuntimeStateManager
from fastapi.testclient import TestClient
from app.main import app

def test_boot_seeds_fleet():
    """
    Test 6a: A freshly constructed RuntimeStateManager results in state.stations 
    and state.evs being non-empty and internally consistent.
    """
    # Create fresh state manager to simulate app boot
    state_manager = RuntimeStateManager()
    state_manager.reset_state() # deps.py does this on boot
    
    state = state_manager.get_state()
    
    assert len(state.stations) == 6
    assert len(state.evs) == 8
    
    # Internal consistency:
    # 1. Every occupied station's connected_ev_id matches a real EV
    occupied_stations = [s for s in state.stations if s.occupancy]
    ev_ids = {ev.ev_id for ev in state.evs}
    for st in occupied_stations:
        assert st.connected_ev_id in ev_ids
        
    # 2. Every EV with a station_id points at a real station
    station_ids = {st.station_id for st in state.stations}
    for ev in state.evs:
        if ev.station_id:
            assert ev.station_id in station_ids


def test_simulation_reset_repopulates_fleet():
    """
    Test 6b & 6c: POST /simulation/reset returns a SystemState with a populated
    fleet/stations containing all 5 vehicle types.
    """
    client = TestClient(app)
    
    # Send reset
    response = client.post("/api/simulation/reset")
    assert response.status_code == 200
    
    data = response.json()
    
    # Check fleet size matches expectations (6 stations, 8 EVs)
    assert len(data["stations"]) == 6
    assert len(data["evs"]) == 8
    
    # Test 6c: Ensure all 5 vehicle types are present
    vehicle_types = {ev["vehicle_type"] for ev in data["evs"]}
    expected_types = {"SUV", "SEDAN", "HATCHBACK", "SCOOTER", "BIKE"}
    
    # Allow for title case if mapped that way, but pydantic model EV expects specific string values
    # Let's uppercase to be safe
    vehicle_types_upper = {vt.upper() for vt in vehicle_types}
    assert expected_types.issubset(vehicle_types_upper)
