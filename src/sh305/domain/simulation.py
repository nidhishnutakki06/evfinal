from pydantic import BaseModel, Field
from sh305.domain.enums import SimulationStatus


class Simulation(BaseModel):
    """
    Simulation progression and status metadata.
    Environmental conditions (weather, time of day) are maintained separately in Environment.
    """
    simulation_time: float = Field(0.0, ge=0.0, description="Current simulation clock in hours (e.g., 8.0 for 08:00)")
    start_time: float = Field(0.0, ge=0.0, description="Simulation run start time in hours")
    end_time: float = Field(24.0, ge=0.0, description="Simulation run end time in hours")
    simulation_status: SimulationStatus = Field(default=SimulationStatus.IDLE, description="Execution status of simulation engine")
