"""
Vehicle profile specifications for SH-305.

DISCLAIMER:
Synthetic demo parameters for SH-305. These are not manufacturer specifications
and are not sourced from a real-world dataset.
"""

from typing import Dict
from pydantic import BaseModel, Field
from sh305.domain.enums import VehicleType

VEHICLE_PROFILE_DISCLAIMER: str = (
    "Synthetic demo parameters for SH-305. These are not manufacturer specifications "
    "and are not sourced from a real-world dataset."
)


class VehicleProfile(BaseModel):
    """
    Standardized synthetic specification for a vehicle archetype.
    """
    vehicle_type: VehicleType = Field(..., description="Vehicle category")
    battery_capacity_kwh: float = Field(..., gt=0.0, description="Nominal battery capacity in kWh")
    expected_range_km: float = Field(..., gt=0.0, description="Estimated full-charge driving range in km")
    min_charging_rate_kw: float = Field(..., ge=0.0, description="Minimum operable charging rate in kW")
    max_charging_rate_kw: float = Field(..., ge=0.0, description="Maximum onboard AC/DC charging acceptance rate in kW")
    description: str = Field(default="", description="Archetype notes and synthetic demo assumptions")


VEHICLE_PROFILES: Dict[VehicleType, VehicleProfile] = {
    VehicleType.SUV: VehicleProfile(
        vehicle_type=VehicleType.SUV,
        battery_capacity_kwh=75.0,
        expected_range_km=420.0,
        min_charging_rate_kw=3.3,
        max_charging_rate_kw=11.0,
        description="Large passenger EV with 75 kWh battery pack (Synthetic demo parameters).",
    ),
    VehicleType.SEDAN: VehicleProfile(
        vehicle_type=VehicleType.SEDAN,
        battery_capacity_kwh=60.0,
        expected_range_km=380.0,
        min_charging_rate_kw=3.3,
        max_charging_rate_kw=11.0,
        description="Mid-size executive sedan with 60 kWh battery pack (Synthetic demo parameters).",
    ),
    VehicleType.HATCHBACK: VehicleProfile(
        vehicle_type=VehicleType.HATCHBACK,
        battery_capacity_kwh=35.0,
        expected_range_km=240.0,
        min_charging_rate_kw=2.3,
        max_charging_rate_kw=7.4,
        description="Compact urban commuter with 35 kWh battery pack (Synthetic demo parameters).",
    ),
    VehicleType.SCOOTER: VehicleProfile(
        vehicle_type=VehicleType.SCOOTER,
        battery_capacity_kwh=3.5,
        expected_range_km=85.0,
        min_charging_rate_kw=0.8,
        max_charging_rate_kw=2.2,
        description="Lightweight 2-wheeler electric scooter with 3.5 kWh battery (Synthetic demo parameters).",
    ),
    VehicleType.BIKE: VehicleProfile(
        vehicle_type=VehicleType.BIKE,
        battery_capacity_kwh=4.5,
        expected_range_km=110.0,
        min_charging_rate_kw=1.0,
        max_charging_rate_kw=3.3,
        description="Electric motorcycle / utility 2-wheeler with 4.5 kWh battery (Synthetic demo parameters).",
    ),
}


def get_vehicle_profile(vehicle_type: VehicleType) -> VehicleProfile:
    """Retrieve canonical profile for vehicle type."""
    if vehicle_type not in VEHICLE_PROFILES:
        raise KeyError(f"No profile registered for vehicle type: {vehicle_type}")
    return VEHICLE_PROFILES[vehicle_type]
