from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List
import asyncio
import logging

from app.models.pydantic_state import SystemState
from app.services.state_manager import RuntimeStateManager
from app.api.deps import get_state_manager

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages active WebSocket clients and broadcasts the canonical SystemState.
    It does not own state; it retrieves it authoritatively via RuntimeStateManager.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_state(self, state: SystemState):
        if not self.active_connections:
            return
            
        # Pydantic native serialization to dict, strictly mimicking the REST contract
        state_dict = state.model_dump(mode='json')
        
        async def send(ws: WebSocket):
            try:
                await ws.send_json(state_dict)
            except Exception as e:
                logger.error(f"Failed to send state to websocket: {e}")
                self.disconnect(ws)
                
        # Send to all connected clients concurrently
        await asyncio.gather(*(send(ws) for ws in self.active_connections))

# Singleton connection manager for the app
connection_manager = ConnectionManager()

def get_connection_manager() -> ConnectionManager:
    return connection_manager

# Router
router = APIRouter(tags=["Realtime"])

@router.websocket("/ws/state")
async def websocket_endpoint(
    websocket: WebSocket, 
    state_manager: RuntimeStateManager = Depends(get_state_manager),
    manager: ConnectionManager = Depends(get_connection_manager)
):
    await manager.connect(websocket)
    try:
        # Initial authoritative state send
        current_state = state_manager.get_state()
        await websocket.send_json(current_state.model_dump(mode='json'))
        
        # Keep connection open. 
        # For this phase, client messages are NOT authoritative.
        while True:
            # We wait for messages but do NOT mutate SystemState based on them.
            data = await websocket.receive_text()
            # Explicitly ignored to protect backend authority.
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
