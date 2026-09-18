import pytest
from pydantic import ValidationError
from sh305.domain.enums import (
    VehicleType,
    StationStatus,
    DeadlineStatus,
    WeatherCondition,
    TimeOfDay,
    UserUrgency,
    SafetyState,
    SimulationStatus,
)
from sh305.domain.ev import EV
from sh305.domain.station import Station
from sh305.domain.building import Building
from sh305.domain.environment import Solar, Environment
from sh305.domain.grid import Grid
from sh305.domain.simulation import Simulation


def test_deadline_status_enum_values():
    """Verify DeadlineStatus contains exactly ON_TRACK, AT_RISK, UNABLE."""
    enum_members = [m.value for m in DeadlineStatus]
    assert set(enum_members) == {"ON_TRACK", "AT_RISK", "UNABLE"}
    assert len(DeadlineStatus) == 3


def test_simulation_environment_state_separation():
    """Verify that Simulation and Environment have separated responsibilities with no duplicates."""
    sim_fields = set(Simulation.model_fields.keys())
    env_fields = set(Environment.model_fields.keys())

    # Environment should NOT have simulation_time, start_time, end_time, simulation_status
    assert "simulation_time" not in env_fields
    assert "start_time" not in env_fields
    assert "end_time" not in env_fields
    assert "simulation_status" not in env_fields

    # Simulation should NOT duplicate weather or time_of_day
    assert "weather" not in sim_fields
    assert "time_of_day" not in sim_fields
    assert "current_weather" not in sim_fields

    # No field intersection between Simulation and Environment
    assert sim_fields.isdisjoint(env_fields)


def test_ev_model_valid_creation():
    """Verify valid creation of EV model with required and default fields."""
    ev = EV(
        ev_id="EV-001",
        vehicle_type=VehicleType.SUV,
        battery_capacity_kwh=75.0,
        expected_range_km=420.0,
        current_soc=45.0,
        requested_travel_distance_km=120.0,
        arrival_time=8.5,
        departure_time=17.5,
        min_charging_rate_kw=3.3,
        max_charging_rate_kw=11.0,
    )
    assert ev.ev_id == "EV-001"
    assert ev.vehicle_type == VehicleType.SUV
    assert ev.current_soc == 45.0
    # Future calculated values must remain at safe uncomputed placeholders
    assert ev.target_soc is None
    assert ev.energy_required_kwh == 0.0
    assert ev.time_remaining_hours == 0.0
    assert ev.required_average_power_kw == 0.0
    assert ev.priority_score == 0.0
    assert ev.estimated_completion_time is None
    assert ev.estimated_soc_at_departure is None
    assert ev.deadline_status is None
    assert ev.physical_feasibility is None
    assert ev.current_allocation_feasibility is None
    assert ev.predictive_risk_flag is False
    assert ev.reason == ""


def test_ev_soc_validation_rejects_out_of_bounds():
    """Verify invalid SoC values (< 0 or > 100) are rejected."""
    # current_soc < 0
    with pytest.raises(ValidationError):
        EV(
            ev_id="EV-ERR1",
            vehicle_type=VehicleType.SEDAN,
            battery_capacity_kwh=60.0,
            expected_range_km=380.0,
            current_soc=-5.0,
            arrival_time=8.0,
            departure_time=16.0,
            max_charging_rate_kw=11.0,
        )

    # current_soc > 100
    with pytest.raises(ValidationError):
        EV(
            ev_id="EV-ERR2",
            vehicle_type=VehicleType.SEDAN,
            battery_capacity_kwh=60.0,
            expected_range_km=380.0,
            current_soc=105.0,
            arrival_time=8.0,
            departure_time=16.0,
            max_charging_rate_kw=11.0,
        )

    # target_soc > 100
    with pytest.raises(ValidationError):
        EV(
            ev_id="EV-ERR3",
            vehicle_type=VehicleType.SEDAN,
            battery_capacity_kwh=60.0,
            expected_range_km=380.0,
            current_soc=50.0,
            target_soc=120.0,
            arrival_time=8.0,
            departure_time=16.0,
            max_charging_rate_kw=11.0,
        )


def test_negative_physical_quantities_rejected():
    """Verify negative physical quantities (battery capacity, charging rates, grid limit) are rejected."""
    # Negative battery capacity
    with pytest.raises(ValidationError):
        EV(
            ev_id="EV-ERR4",
            vehicle_type=VehicleType.SEDAN,
            battery_capacity_kwh=-60.0,
            expected_range_km=380.0,
            current_soc=50.0,
            arrival_time=8.0,
            departure_time=16.0,
            max_charging_rate_kw=11.0,
        )

    # Negative charging rate
    with pytest.raises(ValidationError):
        Station(
            station_id="CS-ERR",
            station_capacity_kw=22.0,
            min_charging_rate_kw=-1.0,
            max_charging_rate_kw=22.0,
        )

    # Negative or zero grid configured limit
    with pytest.raises(ValidationError):
        Grid(
            configured_limit_kw=0.0,
            active_limit_kw=100.0,
            current_import_kw=20.0,
            available_capacity_kw=80.0,
        )

    with pytest.raises(ValidationError):
        Grid(
            configured_limit_kw=-150.0,
            active_limit_kw=100.0,
            current_import_kw=20.0,
            available_capacity_kw=80.0,
        )

    # Negative building demand
    with pytest.raises(ValidationError):
        Building(
            ac_demand_kw=-10.0,
            lights_demand_kw=10.0,
            lifts_demand_kw=5.0,
            appliances_demand_kw=5.0,
        )

    # Negative solar generation
    with pytest.raises(ValidationError):
        Solar(
            generation_kw=-5.0,
            usable_solar_kw=0.0,
            excess_solar_kw=0.0,
        )


def test_building_total_demand_calculation():
    """Verify that building total demand sums components correctly."""
    b = Building(
        ac_demand_kw=25.0,
        lights_demand_kw=10.0,
        lifts_demand_kw=5.0,
        appliances_demand_kw=10.0,
    )
    assert b.total_demand_kw == 50.0
