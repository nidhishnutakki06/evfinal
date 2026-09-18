import pytest
from sh305.domain.ev import EV
from sh305.domain.station import Station
from sh305.domain.enums import VehicleType
from sh305.engine import feasibility

@pytest.fixture
def base_ev():
    return EV(
        ev_id="EV-1",
        vehicle_type=VehicleType.SUV,
        battery_capacity_kwh=60.0,
        expected_range_km=300.0,
        current_soc=20.0,
        arrival_time=8.0,
        departure_time=17.0,
        max_charging_rate_kw=11.0
    )

@pytest.fixture
def base_station():
    return Station(
        station_id="CS-1",
        station_capacity_kw=22.0,
        max_charging_rate_kw=7.4
    )

def test_critical_numeric_case_c(base_ev, base_station):
    # EV max = 11, Station max = 7.4 -> Effective max = 7.4
    eff = feasibility.calculate_effective_max(base_ev, base_station)
    assert eff == 7.4

def test_critical_numeric_case_d(base_ev):
    # required average = 8 kW, effective max = 11 kW, current allocation = 4 kW
    # Physical = True, Current = False
    base_ev.energy_required_kwh = 24.0
    base_ev.time_remaining_hours = 3.0 # Requires 8kW average
    base_ev.current_charging_rate_kw = 4.0
    
    phys = feasibility.calculate_physical_feasibility(base_ev, effective_max_kw=11.0)
    curr = feasibility.calculate_current_allocation_feasibility(base_ev)
    
    assert phys is True
    assert curr is False

def test_no_station_effective_max(base_ev):
    eff = feasibility.calculate_effective_max(base_ev, None)
    assert eff == 0.0

def test_already_at_target_feasibility(base_ev):
    base_ev.energy_required_kwh = 0.0
    base_ev.time_remaining_hours = 5.0
    
    phys = feasibility.calculate_physical_feasibility(base_ev, effective_max_kw=11.0)
    curr = feasibility.calculate_current_allocation_feasibility(base_ev)
    
    assert phys is True
    assert curr is True

def test_zero_time_remaining_feasibility(base_ev):
    base_ev.energy_required_kwh = 10.0
    base_ev.time_remaining_hours = 0.0
    base_ev.current_charging_rate_kw = 11.0
    
    phys = feasibility.calculate_physical_feasibility(base_ev, effective_max_kw=11.0)
    curr = feasibility.calculate_current_allocation_feasibility(base_ev)
    
    assert phys is False
    assert curr is False

def test_negative_time_remaining_feasibility(base_ev):
    base_ev.energy_required_kwh = 10.0
    base_ev.time_remaining_hours = -1.0
    base_ev.current_charging_rate_kw = 11.0
    
    phys = feasibility.calculate_physical_feasibility(base_ev, effective_max_kw=11.0)
    curr = feasibility.calculate_current_allocation_feasibility(base_ev)
    
    assert phys is False
    assert curr is False
