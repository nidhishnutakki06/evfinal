from typing import List, Dict
from pydantic import BaseModel, Field
from sh305.domain.simulation import Simulation
from sh305.domain.environment import Environment, Solar
from sh305.domain.grid import Grid
from sh305.domain.building import Building
from sh305.domain.station import Station
from sh305.domain.ev import EV


class SystemState(BaseModel):
    """
    Canonical system state representing the entire SH-305 microgrid and charging ecosystem
    at a specific simulation time slice. Downstream optimization, simulation, and predictive
    phases evaluate and update this unified state.
    """
    simulation: Simulation = Field(..., description="Simulation clock and execution state")
    environment: Environment = Field(..., description="Ambient weather and daylight conditions")
    grid: Grid = Field(..., description="Utility grid connection and capacity limits")
    building: Building = Field(..., description="Building non-EV electrical loads")
    solar: Solar = Field(..., description="Solar PV generation and utilization")
    stations: List[Station] = Field(default_factory=list, description="Charging station network")
    evs: List[EV] = Field(default_factory=list, description="Registered electric vehicles")
    allocations: Dict[str, float] = Field(default_factory=dict, description="Active power dispatch allocations by station ID")
    alerts: List[str] = Field(default_factory=list, description="Active system alerts and warnings")
    strategy: str = Field(default="BALANCED", description="Active optimization and allocation strategy name")
    emergency: bool = Field(default=False, description="Global emergency mode status")
