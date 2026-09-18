import pytest
from sh305.domain.ev import EV
from sh305.domain.enums import VehicleType
from sh305.engine import requirements

@pytest.fixture
def base_ev():
    return EV(
        ev_id="EV-1",
        vehicle_type=VehicleType.SUV,
        battery_capacity_kwh=60.0,
        expected_range_km=300.0,
        current_soc=20.0,
        requested_travel_distance_km=90.0,  # 30% of range
        arrival_time=8.0,
        departure_time=17.0,
        max_charging_rate_kw=11.0
    )

def test_target_soc_calculation(base_ev):
    # Trip = 30% SOC. Current = 20%. Reserve = 10%
    # Target = max(20, 30+10) = 40%
    target_soc = requirements.calculate_target_soc(base_ev, reserve_percent=10.0)
    assert target_soc == 40.0

def test_target_soc_not_below_current(base_ev):
    base_ev.current_soc = 60.0
    base_ev.requested_travel_distance_km = 30.0 # 10% trip
    # Target = max(60, 10+10) = 60%
    target_soc = requirements.calculate_target_soc(base_ev, reserve_percent=10.0)
    assert target_soc == 60.0

def test_target_soc_capped_at_100(base_ev):
    base_ev.requested_travel_distance_km = 300.0 # 100% trip
    # Target = max(20, 100+10) = 110, capped at 100%
    target_soc = requirements.calculate_target_soc(base_ev, reserve_percent=10.0)
    assert target_soc == 100.0

def test_energy_requirement(base_ev):
    # Current = 20%, Target = 50%
    # Required = 30% of 60kWh = 18kWh
    base_ev.target_soc = 50.0
    energy = requirements.calculate_energy_required(base_ev)
    assert energy == 18.0

def test_already_at_target_energy(base_ev):
    base_ev.current_soc = 60.0
    base_ev.target_soc = 50.0
    energy = requirements.calculate_energy_required(base_ev)
    assert energy == 0.0

def test_time_remaining(base_ev):
    time = requirements.calculate_time_remaining(base_ev, simulation_time=9.0)
    assert time == 8.0

def test_zero_time_remaining(base_ev):
    time = requirements.calculate_time_remaining(base_ev, simulation_time=17.0)
    assert time == 0.0

def test_negative_time_remaining(base_ev):
    time = requirements.calculate_time_remaining(base_ev, simulation_time=18.0)
    assert time == -1.0

def test_required_average_power(base_ev):
    # Required = 18kWh, Time = 3h -> Power = 6kW
    base_ev.energy_required_kwh = 18.0
    base_ev.time_remaining_hours = 3.0
    power = requirements.calculate_required_power(base_ev)
    assert power == 6.0

def test_required_average_power_zero_time(base_ev):
    base_ev.energy_required_kwh = 18.0
    base_ev.time_remaining_hours = 0.0
    power = requirements.calculate_required_power(base_ev)
    assert power == 0.0

def test_completion_estimate(base_ev):
    base_ev.energy_required_kwh = 22.0
    base_ev.current_charging_rate_kw = 11.0
    # Time needed = 2h. Sim time = 10.0. Completion = 12.0
    completion = requirements.estimate_completion_time(base_ev, simulation_time=10.0)
    assert completion == 12.0

def test_completion_estimate_zero_rate(base_ev):
    base_ev.energy_required_kwh = 22.0
    base_ev.current_charging_rate_kw = 0.0
    completion = requirements.estimate_completion_time(base_ev, simulation_time=10.0)
    assert completion is None

def test_soc_at_departure_projection(base_ev):
    base_ev.current_soc = 20.0
    base_ev.current_charging_rate_kw = 10.0
    base_ev.time_remaining_hours = 3.0
    # Adds 30kWh. 30kWh of 60kWh = 50%. Final SOC = 70%.
    soc = requirements.estimate_soc_at_departure(base_ev)
    assert soc == 70.0

def test_soc_at_departure_capped_at_100(base_ev):
    base_ev.current_soc = 80.0
    base_ev.current_charging_rate_kw = 20.0
    base_ev.time_remaining_hours = 4.0
    # Adds 80kWh -> >100%. Capped at 100%.
    soc = requirements.estimate_soc_at_departure(base_ev)
    assert soc == 100.0

def test_critical_numeric_case_a(base_ev):
    # Battery = 60 kWh, Current SoC = 20%, Target SoC = 50%, Expected energy = 18 kWh
    base_ev.battery_capacity_kwh = 60.0
    base_ev.current_soc = 20.0
    base_ev.target_soc = 50.0
    assert requirements.calculate_energy_required(base_ev) == 18.0

def test_critical_numeric_case_b(base_ev):
    # Energy required = 18 kWh, Time remaining = 3 hours, Expected required power = 6 kW
    base_ev.energy_required_kwh = 18.0
    base_ev.time_remaining_hours = 3.0
    assert requirements.calculate_required_power(base_ev) == 6.0
