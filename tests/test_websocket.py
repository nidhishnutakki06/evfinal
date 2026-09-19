import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_state_manager
from app.api.websocket import get_connection_manager

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_state():
    # Guarantee clean state
    manager = get_state_manager()
    manager.reset_state()
    # Guarantee clean connections
    ws_manager = get_connection_manager()
    ws_manager.active_connections.clear()
    yield

def test_websocket_connection_and_initial_state():
    with client.websocket_connect("/ws/state") as websocket:
        data = websocket.receive_json()
        
        # Verify every canonical top-level section is present
        expected_keys = [
            "simulation", "environment", "grid", "building", "solar", 
            "stations", "evs", "allocations", "alerts", "strategy", "emergency"
        ]
        for key in expected_keys:
            assert key in data
            
        # Verify exact equivalence to RuntimeStateManager
        manager = get_state_manager()
        assert manager.get_state().model_dump(mode="json") == data

def test_multiple_clients_and_broadcast():
    with client.websocket_connect("/ws/state") as ws1, \
         client.websocket_connect("/ws/state") as ws2:
             
        # Consume initial state dispatches
        ws1.receive_json()
        ws2.receive_json()
        
        # Trigger REST mutation (validly updates SystemState and triggers broadcast)
        response = client.post("/api/simulation/start")
        assert response.status_code == 200
        
        # Both WebSocket clients should receive the broadcasted update
        msg1 = ws1.receive_json()
        msg2 = ws2.receive_json()
        
        assert msg1["simulation"]["is_running"] is True
        assert msg2["simulation"]["is_running"] is True
        
        # Prove REST and WebSocket broadcast structures are identical
        assert msg1 == response.json()

def test_disconnect_handling():
    ws_manager = get_connection_manager()
    
    with client.websocket_connect("/ws/state") as ws:
        assert len(ws_manager.active_connections) == 1
        ws.receive_json()
        
    # The endpoint catches WebSocketDisconnect and cleans up
    assert len(ws_manager.active_connections) == 0

def test_disconnected_client_does_not_break_others():
    ws_manager = get_connection_manager()
    with client.websocket_connect("/ws/state") as ws1:
        ws1.receive_json()
        
        with client.websocket_connect("/ws/state") as ws2:
            ws2.receive_json()
            
            # Simulate a broken/disconnected client while leaving ws2 active
            ws1.close()
            
            # Trigger state change
            client.post("/api/simulation/start")
            
            # ws2 must still correctly receive broadcasts
            msg2 = ws2.receive_json()
            assert msg2["simulation"]["is_running"] is True
            # Now ws1 is definitely disconnected and removed
            assert len(ws_manager.active_connections) == 1

def test_client_messages_do_not_mutate_state():
    with client.websocket_connect("/ws/state") as ws:
        ws.receive_json() # consume initial
        
        manager = get_state_manager()
        initial_dict = manager.get_state().model_dump(mode="json")
        
        # Attempt to inject invalid malformed structural data and explicit mutations
        ws.send_text("Arbitrary Frontend String")
        ws.send_json({"grid": {"active_limit": 9999.0}})
        
        # Verify the backend ignores it completely (since it expects REST control)
        current_dict = manager.get_state().model_dump(mode="json")
        assert initial_dict == current_dict

def test_rest_websocket_equivalence():
    with client.websocket_connect("/ws/state") as ws:
        ws_data = ws.receive_json()
        rest_data = client.get("/api/state").json()
        
        # Emphasizes: "The only difference should be transport."
        assert ws_data == rest_data
