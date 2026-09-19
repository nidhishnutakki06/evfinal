from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional

class AlertCategory(str, Enum):
    A3_PREDICTIVE_RISK = "A3_PREDICTIVE_RISK"
    EMERGENCY_EVENT = "EMERGENCY_EVENT"
    SAFETY_EVENT = "SAFETY_EVENT"

class StrategyType(str, Enum):
    DEADLINE_FIRST = "DEADLINE_FIRST"
    SOLAR_FIRST = "SOLAR_FIRST"
    GRID_SAFETY_FIRST = "GRID_SAFETY_FIRST"

class Simulation(BaseModel):
    simulation_time: float = 0.0
    is_running: bool = False
    timestep: float = 1.0

class Environment(BaseModel):
    weather: str = "Sunny"
    time_of_day: str = "Morning"

class Grid(BaseModel):
    configured_limit: float = Field(..., ge=0.0)
    active_limit: float = Field(..., ge=0.0)
    grid_import: float = Field(0.0, ge=0.0)
    available_capacity: float = 0.0
    safety_state: str = "SAFE"

class Building(BaseModel):
    ac_demand: float = Field(0.0, ge=0.0)
    lights_demand: float = Field(0.0, ge=0.0)
    lifts_demand: float = Field(0.0, ge=0.0)
    appliances_demand: float = Field(0.0, ge=0.0)
    total_building_demand: float = Field(0.0, ge=0.0)

class Solar(BaseModel):
    generation: float = Field(0.0, ge=0.0)
    usable_solar: float = Field(0.0, ge=0.0)
    excess_solar: float = Field(0.0, ge=0.0)

class Station(BaseModel):
    station_id: str
    occupancy: bool = False
    connected_ev_id: Optional[str] = None
    capacity: float = Field(..., gt=0.0)
    minimum_charging_rate: float = Field(0.0, ge=0.0)
    maximum_charging_rate: float = Field(..., ge=0.0)
    allocated_power: float = Field(0.0, ge=0.0)
    status: str = "AVAILABLE"

    @model_validator(mode='after')
    def check_min_max_rates(self) -> 'Station':
        if self.minimum_charging_rate > self.maximum_charging_rate:
            raise ValueError('minimum_charging_rate cannot be greater than maximum_charging_rate')
        return self

class EV(BaseModel):
    ev_id: str
    vehicle_type: str
    battery_capacity: float = Field(..., gt=0.0)
    range: float = Field(0.0, ge=0.0)
    current_soc: float = Field(..., ge=0.0, le=100.0)
    target_soc: float = Field(..., ge=0.0, le=100.0)
    requested_travel_distance: float = Field(0.0, ge=0.0)
    arrival: float
    departure: float
    minimum_rate: float = Field(0.0, ge=0.0)
    maximum_rate: float = Field(..., ge=0.0)
    current_rate: float = Field(0.0, ge=0.0)
    energy_required: float = Field(0.0, ge=0.0)
    time_remaining: float = Field(0.0, ge=0.0)
    required_average_power: float = Field(0.0, ge=0.0)
    urgency: str = "NORMAL"
    priority_score: float = 0.0
    estimated_completion: float = 0.0
    estimated_soc_at_departure: float = 0.0
    deadline_status: str = "ON_TRACK"
    physical_feasibility: bool = True
    current_allocation_feasibility: bool = True
    a3_risk: str = "NONE"
    a2_reason: str = "INIT"
    grid_contribution: float = Field(0.0, ge=0.0)
    solar_contribution: float = Field(0.0, ge=0.0)
    station_id: Optional[str] = None

    @model_validator(mode='after')
    def validate_ev_constraints(self) -> 'EV':
        if self.minimum_rate > self.maximum_rate:
            raise ValueError('minimum_rate cannot be greater than maximum_rate')
        if self.arrival > self.departure:
            raise ValueError('arrival time cannot be strictly greater than departure time')
        return self

class Allocation(BaseModel):
    ev_id: str
    allocated_rate: float = Field(0.0, ge=0.0)
    allocation_status: str = "PENDING"
    grid_contribution: float = Field(0.0, ge=0.0)
    solar_contribution: float = Field(0.0, ge=0.0)

class Alert(BaseModel):
    alert_id: str
    type: AlertCategory
    message: str
    timestamp: float
    severity: str

class Strategy(BaseModel):
    active_strategy: StrategyType = StrategyType.DEADLINE_FIRST

class Emergency(BaseModel):
    emergency_active_state: bool = False
    emergency_limit: float = Field(..., ge=0.0)

class SystemState(BaseModel):
    simulation: Simulation = Field(default_factory=Simulation)
    environment: Environment = Field(default_factory=Environment)
    grid: Grid
    building: Building = Field(default_factory=Building)
    solar: Solar = Field(default_factory=Solar)
    stations: List[Station] = Field(default_factory=list)
    evs: List[EV] = Field(default_factory=list)
    allocations: List[Allocation] = Field(default_factory=list)
    alerts: List[Alert] = Field(default_factory=list)
    strategy: Strategy = Field(default_factory=Strategy)
    emergency: Emergency
