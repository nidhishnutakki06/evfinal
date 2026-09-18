import pytest
from sh305.synthetic.generator import SyntheticDataGenerator
from sh305.domain.enums import VehicleType, StationStatus, WeatherCondition, TimeOfDay
from sh305.domain.system_state import SystemState


@pytest.fixture
def generator():
    return SyntheticDataGenerator(seed=42)


def test_generate_stations_default_count_is_eight(generator):
    """Verify default station count is 8 and is configurable."""
    stations = generator.generate_stations()
    assert len(stations) == 8

    # Verify configurable station count
    stations_custom = generator.generate_stations(count=4)
    assert len(stations_custom) == 4


def test_station_fields_and_validity(generator):
    """Verify generated stations contain all required fields with physical validity."""
    stations = generator.generate_stations(count=8)
    for s in stations:
        assert s.station_id.startswith("CS-")
        assert s.station_capacity_kw > 0.0
        assert s.min_charging_rate_kw >= 0.0
        assert s.max_charging_rate_kw >= s.min_charging_rate_kw
        assert s.status == StationStatus.AVAILABLE
        assert s.occupied is False
        assert s.connected_ev_id is None
        assert s.current_allocated_power_kw == 0.0
        assert s.grid_contribution_kw == 0.0
        assert s.renewable_contribution_kw == 0.0


def test_generate_evs_fields_and_variation(generator):
    """Verify generated EVs contain required fields and meaningful variation."""
    evs = generator.generate_evs(count=8)
    assert len(evs) == 8

    vehicle_types_seen = set()
    socs = []
    travel_reqs = []

    for ev in evs:
        # Check required fields
        assert ev.ev_id.startswith("EV-")
        assert ev.battery_capacity_kwh > 0.0
        assert ev.expected_range_km > 0.0
        assert 0.0 <= ev.current_soc <= 100.0
        assert ev.requested_travel_distance_km >= 0.0
        assert ev.arrival_time < ev.departure_time
        assert ev.min_charging_rate_kw >= 0.0
        assert ev.max_charging_rate_kw > 0.0

        # Uncomputed calculated fields check
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

        vehicle_types_seen.add(ev.vehicle_type)
        socs.append(ev.current_soc)
        travel_reqs.append(ev.requested_travel_distance_km)

    # Ensure meaningful diversity across generated fleet
    assert len(vehicle_types_seen) >= 4
    assert len(set(socs)) > 1
    assert len(set(travel_reqs)) > 1


def test_building_baseline_validity(generator):
    """Verify generated building baseline contains required fields with non-negative loads."""
    b = generator.generate_building_baseline()
    assert b.ac_demand_kw >= 0.0
    assert b.lights_demand_kw >= 0.0
    assert b.lifts_demand_kw >= 0.0
    assert b.appliances_demand_kw >= 0.0
    assert b.total_demand_kw == (b.ac_demand_kw + b.lights_demand_kw + b.lifts_demand_kw + b.appliances_demand_kw)


def test_solar_baseline_validity(generator):
    """Verify generated solar baseline state is non-negative and consistent."""
    s = generator.generate_solar_baseline()
    assert s.generation_kw >= 0.0
    assert s.usable_solar_kw >= 0.0
    assert s.excess_solar_kw >= 0.0


def test_environment_baseline_validity(generator):
    """Verify generated environment baseline contains valid conditions."""
    env = generator.generate_environment_baseline()
    assert env.weather in list(WeatherCondition)
    assert env.time_of_day in list(TimeOfDay)


def test_grid_baseline_validity(generator):
    """Verify generated grid baseline contains valid positive limits and available capacity."""
    grid = generator.generate_grid_baseline()
    assert grid.configured_limit_kw > 0.0
    assert grid.active_limit_kw > 0.0
    assert grid.current_import_kw >= 0.0
    assert grid.available_capacity_kw == (grid.active_limit_kw - grid.current_import_kw)


def test_system_state_construction(generator):
    """Verify that canonical SystemState can be constructed with all sub-models."""
    state = generator.generate_initial_system_state(ev_count=8, station_count=8)
    assert isinstance(state, SystemState)
    assert len(state.stations) == 8
    assert len(state.evs) == 8
    assert state.simulation.simulation_time == 8.0
    assert state.environment.weather == WeatherCondition.SUNNY
    assert state.grid.configured_limit_kw == 150.0
    assert state.building.total_demand_kw == 60.0
    assert state.solar.generation_kw == 40.0
    assert state.strategy == "BALANCED"
    assert state.emergency is False
    assert len(state.allocations) == 8
