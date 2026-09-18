from typing import Optional
from pydantic import BaseModel, Field, field_validator
from sh305.domain.enums import VehicleType, UserUrgency, DeadlineStatus


class EV(BaseModel):
    """
    Canonical Electric Vehicle (EV) entity for SH-305.
    
    Includes vehicle battery specifications, state-of-charge, schedule bounds,
    and operational placeholders for downstream optimization and simulation phases.
    Battery is an integral part of the EV entity.
    """
    # Source / Primary Attributes
    ev_id: str = Field(..., description="Unique identifier for the vehicle")
    vehicle_type: VehicleType = Field(..., description="Canonical vehicle classification")
    battery_capacity_kwh: float = Field(..., gt=0, description="Total battery capacity in kWh")
    expected_range_km: float = Field(..., gt=0, description="Expected vehicle range at 100% SoC in km")
    current_soc: float = Field(..., ge=0.0, le=100.0, description="Current State of Charge percentage [0, 100]")
    requested_travel_distance_km: float = Field(0.0, ge=0.0, description="User requested travel distance in km")
    arrival_time: float = Field(..., ge=0.0, description="Arrival simulation time in hours")
    departure_time: float = Field(..., ge=0.0, description="Target departure simulation time in hours")
    min_charging_rate_kw: float = Field(0.0, ge=0.0, description="Minimum acceptable charging rate in kW")
    max_charging_rate_kw: float = Field(..., ge=0.0, description="Maximum onboard/station charging rate in kW")
    current_charging_rate_kw: float = Field(0.0, ge=0.0, description="Current active charging rate in kW")
    user_urgency: UserUrgency = Field(default=UserUrgency.MEDIUM, description="User priority preference")
    station_id: Optional[str] = Field(default=None, description="Connected station ID if currently plugged in")
    grid_contribution_kw: float = Field(default=0.0, ge=0.0, description="Power supplied from utility grid in kW")
    solar_contribution_kw: float = Field(default=0.0, ge=0.0, description="Power supplied from on-site solar in kW")

    # Future Calculated / Optimizer Attributes (Safe uncomputed placeholders in Phase 1)
    target_soc: Optional[float] = Field(default=None, description="Target SoC percentage [0, 100] calculated by downstream engine")
    energy_required_kwh: float = Field(default=0.0, ge=0.0, description="Uncomputed energy requirement placeholder")
    time_remaining_hours: float = Field(default=0.0, description="Time remaining until departure in hours")
    required_average_power_kw: float = Field(default=0.0, ge=0.0, description="Average power needed to hit target SoC")
    priority_score: float = Field(default=0.0, description="Calculated priority score placeholder")
    estimated_completion_time: Optional[float] = Field(default=None, description="Estimated completion timestamp in simulation hours")
    estimated_soc_at_departure: Optional[float] = Field(default=None, description="Estimated departure SoC percentage")
    deadline_status: Optional[DeadlineStatus] = Field(default=None, description="Operational deadline feasibility status")
    physical_feasibility: Optional[bool] = Field(default=None, description="Physical feasibility flag placeholder")
    current_allocation_feasibility: Optional[bool] = Field(default=None, description="Allocation feasibility flag placeholder")
    predictive_risk_flag: bool = Field(default=False, description="A3 predictive risk indicator")
    reason: str = Field(default="", description="Operational reason or allocation diagnostic comment")

    @field_validator("target_soc")
    @classmethod
    def validate_target_soc(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 100.0):
            raise ValueError(f"target_soc must be between 0.0 and 100.0, got {v}")
        return v

    @field_validator("estimated_soc_at_departure")
    @classmethod
    def validate_est_departure_soc(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 100.0):
            raise ValueError(f"estimated_soc_at_departure must be between 0.0 and 100.0, got {v}")
        return v
