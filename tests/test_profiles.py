import pytest
from sh305.domain.enums import VehicleType
from sh305.synthetic.vehicle_profiles import (
    VEHICLE_PROFILES,
    VEHICLE_PROFILE_DISCLAIMER,
    VehicleProfile,
    get_vehicle_profile,
)


def test_all_five_vehicle_profiles_exist():
    """Verify that all five specified vehicle profiles exist."""
    expected_types = {
        VehicleType.SUV,
        VehicleType.SEDAN,
        VehicleType.HATCHBACK,
        VehicleType.SCOOTER,
        VehicleType.BIKE,
    }
    assert set(VEHICLE_PROFILES.keys()) == expected_types
    assert len(VEHICLE_PROFILES) == 5


def test_profile_fields_and_consistency():
    """Verify that each vehicle profile contains all required physical parameters with valid positive values."""
    for v_type, profile in VEHICLE_PROFILES.items():
        assert isinstance(profile, VehicleProfile)
        assert profile.vehicle_type == v_type
        assert profile.battery_capacity_kwh > 0.0
        assert profile.expected_range_km > 0.0
        assert profile.min_charging_rate_kw >= 0.0
        assert profile.max_charging_rate_kw >= profile.min_charging_rate_kw
        assert profile.max_charging_rate_kw > 0.0


def test_profile_retrieval_helper():
    """Test get_vehicle_profile helper and error handling."""
    suv_profile = get_vehicle_profile(VehicleType.SUV)
    assert suv_profile.vehicle_type == VehicleType.SUV
    assert suv_profile.battery_capacity_kwh == 75.0

    with pytest.raises(KeyError):
        get_vehicle_profile("INVALID_TYPE")  # type: ignore


def test_profile_synthetic_disclaimer():
    """Verify that synthetic profiles explicitly include the demo disclaimer."""
    assert "Synthetic demo parameters for SH-305" in VEHICLE_PROFILE_DISCLAIMER
    assert "not manufacturer specifications" in VEHICLE_PROFILE_DISCLAIMER
