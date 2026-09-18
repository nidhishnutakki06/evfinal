import pytest
from sh305.domain.building import Building
from sh305.domain.environment import Solar
from sh305.domain.grid import Grid
from sh305.domain.ev import EV
from sh305.domain.enums import VehicleType
from sh305.engine import energy

def test_critical_numeric_case_e():
    """
    Building = 91 kW
    EV demand = 0 kW
    Solar = 35 kW
    Expected: Site load = 91, Usable solar = 35, Excess solar = 0, Grid import = 56
    """
    building = Building(ac_demand_kw=45.5, lights_demand_kw=12.0, lifts_demand_kw=25.0, appliances_demand_kw=8.5, total_demand_kw=91.0)
    solar = Solar(generation_kw=35.0, usable_solar_kw=0, excess_solar_kw=0)
    evs = []
    
    site_load = energy.calculate_site_load(building, evs)
    assert site_load == 91.0
    
    usable = energy.calculate_usable_solar(solar, site_load)
    assert usable == 35.0
    
    excess = energy.calculate_excess_solar(solar, site_load)
    assert excess == 0.0
    
    grid_import = energy.calculate_grid_import(site_load, usable)
    assert grid_import == 56.0

def test_critical_numeric_case_f():
    """
    Solar > site load
    Expected: Grid import = 0, Excess solar > 0
    """
    building = Building(ac_demand_kw=0, lights_demand_kw=0, lifts_demand_kw=0, appliances_demand_kw=10.0, total_demand_kw=10.0)
    solar = Solar(generation_kw=50.0, usable_solar_kw=0, excess_solar_kw=0)
    evs = []
    
    site_load = energy.calculate_site_load(building, evs)
    usable = energy.calculate_usable_solar(solar, site_load)
    excess = energy.calculate_excess_solar(solar, site_load)
    grid_import = energy.calculate_grid_import(site_load, usable)
    
    assert grid_import == 0.0
    assert excess == 40.0

def test_zero_solar():
    building = Building(ac_demand_kw=0, lights_demand_kw=0, lifts_demand_kw=0, appliances_demand_kw=10.0, total_demand_kw=10.0)
    solar = Solar(generation_kw=0.0, usable_solar_kw=0, excess_solar_kw=0)
    
    site_load = energy.calculate_site_load(building, [])
    usable = energy.calculate_usable_solar(solar, site_load)
    grid_import = energy.calculate_grid_import(site_load, usable)
    
    assert usable == 0.0
    assert grid_import == 10.0

def test_overloaded_candidate_state():
    """
    Building = 90
    EV demand = 40
    Solar = 10
    Grid limit = 100
    Expected: SITE_LOAD = 130, USABLE_SOLAR = 10, GRID_IMPORT = 120, AVAILABLE_GRID_CAPACITY = 0
    """
    building = Building(ac_demand_kw=90.0, lights_demand_kw=0, lifts_demand_kw=0, appliances_demand_kw=0, total_demand_kw=90.0)
    ev = EV(
        ev_id="EV-1", vehicle_type=VehicleType.SUV, battery_capacity_kwh=60.0, expected_range_km=300.0,
        current_soc=20.0, arrival_time=8.0, departure_time=17.0, max_charging_rate_kw=11.0, current_charging_rate_kw=40.0
    )
    solar = Solar(generation_kw=10.0, usable_solar_kw=0, excess_solar_kw=0)
    grid = Grid(configured_limit_kw=100.0, active_limit_kw=100.0, current_import_kw=0, available_capacity_kw=100.0)
    
    site_load = energy.calculate_site_load(building, [ev])
    assert site_load == 130.0
    
    usable = energy.calculate_usable_solar(solar, site_load)
    assert usable == 10.0
    
    grid_import = energy.calculate_grid_import(site_load, usable)
    assert grid_import == 120.0
    
    avail_cap = energy.calculate_available_grid_capacity(grid, grid_import)
    assert avail_cap == 0.0
