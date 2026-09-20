from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, model_validator
from typing import Optional

from app.models.pydantic_state import SystemState, StrategyType, EV
from app.services.state_manager import RuntimeStateManager
from app.services.control import ControlService
from app.api.deps import get_state_manager, get_control_service
from app.api.websocket import get_connection_manager, ConnectionManager

router = APIRouter(prefix="/api", tags=["Control"])

# Explicit Request Schemas
class HealthResponse(BaseModel):
    status: str

class BuildingDemandRequest(BaseModel):
    ac: float = Field(..., ge=0.0)
    lights: float = Field(..., ge=0.0)
    lifts: float = Field(..., ge=0.0)
    appliances: float = Field(..., ge=0.0)

class GridLimitRequest(BaseModel):
    limit: float = Field(..., ge=0.0)

class WeatherRequest(BaseModel):
    weather: str
    time_of_day: Optional[str] = None

class SpawnEVRequest(BaseModel):
    ev_id: str
    vehicle_type: str
    battery_capacity: float = Field(..., gt=0.0)
    target_soc: float = Field(..., ge=0.0, le=100.0)
    requested_travel_distance: float = Field(0.0, ge=0.0)
    arrival: float
    departure: float
    minimum_rate: float = Field(0.0, ge=0.0)
    maximum_rate: float = Field(..., ge=0.0)
    station_id: Optional[str] = None

    @model_validator(mode='after')
    def validate_bounds(self) -> 'SpawnEVRequest':
        if self.minimum_rate > self.maximum_rate:
            raise ValueError('minimum_rate cannot be greater than maximum_rate')
        if self.arrival > self.departure:
            raise ValueError('arrival cannot be strictly greater than departure')
        return self

class SpawnUrgentEVRequest(SpawnEVRequest):
    urgency: str = "URGENT"

class StrategyRequest(BaseModel):
    active_strategy: StrategyType

# Endpoints
@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok")

@router.get("/state", response_model=SystemState)
def get_state(manager: RuntimeStateManager = Depends(get_state_manager)):
    return manager.get_state()

@router.post("/simulation/start", response_model=SystemState)
async def start_simulation(
    control: ControlService = Depends(get_control_service),
    ws_manager: ConnectionManager = Depends(get_connection_manager)
):
    try:
        new_state = control.process_simulation_status(is_running=True)
        await ws_manager.broadcast_state(new_state)
        return new_state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/simulation/pause", response_model=SystemState)
async def pause_simulation(
    control: ControlService = Depends(get_control_service),
    ws_manager: ConnectionManager = Depends(get_connection_manager)
):
    try:
        new_state = control.process_simulation_status(is_running=False)
        await ws_manager.broadcast_state(new_state)
        return new_state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/simulation/reset", response_model=SystemState)
async def reset_simulation(
    control: ControlService = Depends(get_control_service),
    ws_manager: ConnectionManager = Depends(get_connection_manager)
):
    try:
        new_state = control.process_reset_simulation()
        await ws_manager.broadcast_state(new_state)
        return new_state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/control/building-demand", response_model=SystemState)
async def update_building_demand(
    req: BuildingDemandRequest, 
    control: ControlService = Depends(get_control_service),
    ws_manager: ConnectionManager = Depends(get_connection_manager)
):
    try:
        new_state = control.process_building_demand(
            ac=req.ac, lights=req.lights, lifts=req.lifts, appliances=req.appliances
        )
        await ws_manager.broadcast_state(new_state)
        return new_state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/control/grid-limit", response_model=SystemState)
async def update_grid_limit(
    req: GridLimitRequest, 
    control: ControlService = Depends(get_control_service),
    ws_manager: ConnectionManager = Depends(get_connection_manager)
):
    try:
        new_state = control.process_grid_limit(req.limit)
        await ws_manager.broadcast_state(new_state)
        return new_state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/control/weather", response_model=SystemState)
async def update_weather(
    req: WeatherRequest, 
    control: ControlService = Depends(get_control_service),
    ws_manager: ConnectionManager = Depends(get_connection_manager)
):
    try:
        new_state = control.process_weather(req.weather, req.time_of_day)
        await ws_manager.broadcast_state(new_state)
        return new_state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/control/spawn-ev", response_model=SystemState)
async def spawn_ev(
    req: SpawnEVRequest, 
    control: ControlService = Depends(get_control_service),
    ws_manager: ConnectionManager = Depends(get_connection_manager)
):
    try:
        new_state = control.process_spawn_ev(req.model_dump(), is_urgent=False)
        await ws_manager.broadcast_state(new_state)
        return new_state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/control/spawn-urgent-ev", response_model=SystemState)
async def spawn_urgent_ev(
    req: SpawnUrgentEVRequest, 
    control: ControlService = Depends(get_control_service),
    ws_manager: ConnectionManager = Depends(get_connection_manager)
):
    try:
        new_state = control.process_spawn_ev(req.model_dump(), is_urgent=True)
        await ws_manager.broadcast_state(new_state)
        return new_state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/control/strategy", response_model=SystemState)
async def update_strategy(
    req: StrategyRequest, 
    control: ControlService = Depends(get_control_service),
    ws_manager: ConnectionManager = Depends(get_connection_manager)
):
    try:
        new_state = control.process_strategy(req.active_strategy.value)
        await ws_manager.broadcast_state(new_state)
        return new_state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/control/emergency/activate", response_model=SystemState)
async def activate_emergency(
    control: ControlService = Depends(get_control_service),
    ws_manager: ConnectionManager = Depends(get_connection_manager)
):
    try:
        new_state = control.process_emergency_activation(activate=True)
        await ws_manager.broadcast_state(new_state)
        return new_state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/control/emergency/restore", response_model=SystemState)
async def restore_emergency(
    control: ControlService = Depends(get_control_service),
    ws_manager: ConnectionManager = Depends(get_connection_manager)
):
    try:
        new_state = control.process_emergency_activation(activate=False)
        await ws_manager.broadcast_state(new_state)
        return new_state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
