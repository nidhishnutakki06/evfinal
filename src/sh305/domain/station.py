from typing import Optional
from pydantic import BaseModel, Field
from sh305.domain.enums import StationStatus


class Station(BaseModel):
    """
    Charging station model representing physical EVSE supply equipment.
    """
    station_id: str = Field(..., description="Unique station hardware identifier")
    connected_ev_id: Optional[str] = Field(default=None, description="ID of connected EV, if any")
    station_capacity_kw: float = Field(..., ge=0.0, description="Nameplate power delivery capacity in kW")
    min_charging_rate_kw: float = Field(0.0, ge=0.0, description="Minimum operable charging rate in kW")
    max_charging_rate_kw: float = Field(..., ge=0.0, description="Maximum dispatchable charging rate in kW")
    occupied: bool = Field(default=False, description="Physical plug connection state")
    current_allocated_power_kw: float = Field(default=0.0, ge=0.0, description="Active power dispatch in kW")
    status: StationStatus = Field(default=StationStatus.AVAILABLE, description="Operational status of the station")
    grid_contribution_kw: float = Field(default=0.0, ge=0.0, description="Active power supplied from grid in kW")
    renewable_contribution_kw: float = Field(default=0.0, ge=0.0, description="Active power supplied from renewable/solar in kW")
