from pydantic import BaseModel, Field
from sh305.domain.enums import SafetyState


class Grid(BaseModel):
    """
    Utility grid connection and capacity model.
    """
    configured_limit_kw: float = Field(..., gt=0.0, description="Sanctioned contractual grid limit in kW")
    active_limit_kw: float = Field(..., gt=0.0, description="Dynamic operating grid limit under active curtailment/DR in kW")
    current_import_kw: float = Field(default=0.0, ge=0.0, description="Current power import draw from grid in kW")
    available_capacity_kw: float = Field(..., description="Remaining headroom on active grid limit in kW")
    safety_state: SafetyState = Field(default=SafetyState.NORMAL, description="Current grid thermal/transformer safety state")
    emergency_mode: bool = Field(default=False, description="Emergency demand curtailment or microgrid islanding status")
