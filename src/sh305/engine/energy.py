from typing import List
from sh305.domain.building import Building
from sh305.domain.environment import Solar
from sh305.domain.ev import EV
from sh305.domain.grid import Grid

def calculate_site_load(building: Building, evs: List[EV]) -> float:
    """
    Calculates the total site electrical load.
    B = building demand
    P_total = sum of all active EV current charging rates.
    SITE_LOAD = B + P_total
    """
    p_total = sum(ev.current_charging_rate_kw for ev in evs)
    return building.total_demand_kw + p_total

def calculate_usable_solar(solar: Solar, site_load: float) -> float:
    """
    Calculates the usable solar contribution.
    USABLE_SOLAR = min(S, SITE_LOAD)
    """
    return min(solar.generation_kw, site_load)

def calculate_excess_solar(solar: Solar, site_load: float) -> float:
    """
    Calculates excess solar generation (e.g. going to zero or export).
    EXCESS_SOLAR = max(0, S - SITE_LOAD)
    """
    return max(0.0, solar.generation_kw - site_load)

def calculate_grid_import(site_load: float, usable_solar: float) -> float:
    """
    Calculates necessary grid import to meet demand.
    GRID_IMPORT = max(0, SITE_LOAD - USABLE_SOLAR)
    """
    return max(0.0, site_load - usable_solar)

def calculate_available_grid_capacity(grid: Grid, grid_import: float) -> float:
    """
    Calculates remaining available grid capacity.
    AVAILABLE_GRID_CAPACITY = max(0, G - GRID_IMPORT)
    """
    return max(0.0, grid.active_limit_kw - grid_import)
