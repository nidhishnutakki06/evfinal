from pydantic import BaseModel, Field, model_validator


class Building(BaseModel):
    """
    Building electrical load model representing non-EV base loads.
    """
    ac_demand_kw: float = Field(0.0, ge=0.0, description="HVAC/AC electrical load in kW")
    lights_demand_kw: float = Field(0.0, ge=0.0, description="Lighting electrical load in kW")
    lifts_demand_kw: float = Field(0.0, ge=0.0, description="Elevator/lift power demand in kW")
    appliances_demand_kw: float = Field(0.0, ge=0.0, description="General appliance and plug load in kW")
    manual_demand_offset_kw: float = Field(0.0, description="Manual demand offset delta in kW")
    total_demand_kw: float = Field(0.0, ge=0.0, description="Total building non-EV electrical demand in kW")

    @model_validator(mode="before")
    @classmethod
    def compute_total_demand_if_missing(cls, data: dict) -> dict:
        if isinstance(data, dict):
            ac = data.get("ac_demand_kw", 0.0)
            lights = data.get("lights_demand_kw", 0.0)
            lifts = data.get("lifts_demand_kw", 0.0)
            appliances = data.get("appliances_demand_kw", 0.0)
            calculated_total = float(ac + lights + lifts + appliances)
            # If total_demand_kw not explicitly supplied or 0, populate with sum
            if "total_demand_kw" not in data or data["total_demand_kw"] == 0.0:
                data["total_demand_kw"] = calculated_total
        return data
