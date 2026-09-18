from pydantic import BaseModel, Field
from sh305.domain.enums import WeatherCondition, TimeOfDay


class Solar(BaseModel):
    """
    On-site solar generation model.
    """
    generation_kw: float = Field(0.0, ge=0.0, description="Gross active solar PV generation in kW")
    usable_solar_kw: float = Field(0.0, ge=0.0, description="Solar power directed to building and EV loads in kW")
    excess_solar_kw: float = Field(0.0, ge=0.0, description="Curtailment or export-ready surplus solar power in kW")


class Environment(BaseModel):
    """
    Ambient environmental conditions context.
    Simulation timeline parameters are tracked separately in the Simulation model.
    """
    weather: WeatherCondition = Field(default=WeatherCondition.SUNNY, description="Current ambient weather condition")
    time_of_day: TimeOfDay = Field(default=TimeOfDay.MORNING, description="Current diurnal phase")
