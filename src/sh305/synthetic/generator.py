"""
Deterministic Synthetic Data Generator for SH-305.

Generates reproducible synthetic EV profiles, stations, grid limits, building loads,
solar generation, ambient environment, and complete canonical SystemState.
"""

from typing import List, Optional
import numpy as np

from sh305.domain.enums import (
    VehicleType,
    StationStatus,
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
from sh305.domain.system_state import SystemState
from sh305.synthetic.vehicle_profiles import VEHICLE_PROFILES


class SyntheticDataGenerator:
    """
    Deterministic synthetic data generator using an isolated NumPy RNG.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def reset(self, seed: Optional[int] = None) -> None:
        """Reset RNG to fixed seed for determinism."""
        if seed is not None:
            self.seed = seed
        self.rng = np.random.default_rng(self.seed)

    def generate_evs(self, count: int = 8) -> List[EV]:
        """
        Generate deterministic EV fleet with realistic variation.
        
        Calculated fields (target_soc, energy_required_kwh, time_remaining_hours,
        required_average_power_kw, priority_score, estimated_completion_time,
        estimated_soc_at_departure, deadline_status, physical_feasibility,
        current_allocation_feasibility, predictive_risk_flag, reason)
        are initialized with safe uncomputed placeholders.
        """
        archetypes = [
            VehicleType.SUV,
            VehicleType.SEDAN,
            VehicleType.HATCHBACK,
            VehicleType.SCOOTER,
            VehicleType.BIKE,
            VehicleType.SEDAN,
            VehicleType.SUV,
            VehicleType.HATCHBACK,
        ]
        
        evs: List[EV] = []
        for i in range(count):
            v_type = archetypes[i % len(archetypes)]
            profile = VEHICLE_PROFILES[v_type]
            
            # Deterministic variation around profile archetypes
            # Initial SoC between 15% and 75%
            current_soc = round(float(self.rng.uniform(15.0, 75.0)), 1)
            
            # Requested travel distance between 20 km and 85% of maximum expected range
            max_requested = min(profile.expected_range_km * 0.85, 250.0)
            requested_km = round(float(self.rng.uniform(25.0, max_requested)), 1)
            
            # Staggered arrivals (07:30 to 09:45) and departures (16:00 to 19:30)
            arrival = round(float(self.rng.uniform(7.5, 9.75)), 2)
            departure = round(float(self.rng.uniform(16.0, 19.5)), 2)
            
            # Assign varied urgency levels across fleet
            urgency_options = [
                UserUrgency.LOW,
                UserUrgency.MEDIUM,
                UserUrgency.HIGH,
                UserUrgency.CRITICAL,
            ]
            urgency = urgency_options[i % len(urgency_options)]

            ev = EV(
                ev_id=f"EV-{i + 1:03d}",
                vehicle_type=v_type,
                battery_capacity_kwh=profile.battery_capacity_kwh,
                expected_range_km=profile.expected_range_km,
                current_soc=current_soc,
                requested_travel_distance_km=requested_km,
                arrival_time=arrival,
                departure_time=departure,
                min_charging_rate_kw=profile.min_charging_rate_kw,
                max_charging_rate_kw=profile.max_charging_rate_kw,
                current_charging_rate_kw=0.0,
                user_urgency=urgency,
                station_id=None,
                grid_contribution_kw=0.0,
                solar_contribution_kw=0.0,
                # Safe uncomputed placeholders for downstream phases
                target_soc=None,
                energy_required_kwh=0.0,
                time_remaining_hours=0.0,
                required_average_power_kw=0.0,
                priority_score=0.0,
                estimated_completion_time=None,
                estimated_soc_at_departure=None,
                deadline_status=None,
                physical_feasibility=None,
                current_allocation_feasibility=None,
                predictive_risk_flag=False,
                reason="",
            )
            evs.append(ev)
        return evs

    def generate_stations(self, count: int = 8) -> List[Station]:
        """
        Generate network of charging stations.
        Default count is 8 (supporting 1-to-1 hosting for up to 8 EVs).
        Configurable for custom station counts.
        """
        # Power capacities representative of commercial/workplace EVSE chargers:
        # e.g., 22.0 kW AC fast, 11.0 kW standard, 7.4 kW single-phase, 3.3 kW slow
        capacity_tiers = [22.0, 22.0, 11.0, 11.0, 7.4, 7.4, 3.3, 3.3]
        
        stations: List[Station] = []
        for i in range(count):
            cap = capacity_tiers[i % len(capacity_tiers)]
            min_rate = 1.4 if cap >= 7.0 else 0.8
            stations.append(
                Station(
                    station_id=f"CS-{i + 1:02d}",
                    connected_ev_id=None,
                    station_capacity_kw=cap,
                    min_charging_rate_kw=min_rate,
                    max_charging_rate_kw=cap,
                    occupied=False,
                    current_allocated_power_kw=0.0,
                    status=StationStatus.AVAILABLE,
                    grid_contribution_kw=0.0,
                    renewable_contribution_kw=0.0,
                )
            )
        return stations

    def generate_building_baseline(self) -> Building:
        """Generate baseline non-EV building electrical demand."""
        return Building(
            ac_demand_kw=30.0,
            lights_demand_kw=10.0,
            lifts_demand_kw=8.0,
            appliances_demand_kw=12.0,
            total_demand_kw=60.0,
        )

    def generate_solar_baseline(self) -> Solar:
        """Generate baseline solar generation state."""
        return Solar(
            generation_kw=40.0,
            usable_solar_kw=40.0,
            excess_solar_kw=0.0,
        )

    def generate_environment_baseline(self) -> Environment:
        """Generate baseline ambient environment state."""
        return Environment(
            weather=WeatherCondition.SUNNY,
            time_of_day=TimeOfDay.MORNING,
        )

    def generate_simulation_baseline(self) -> Simulation:
        """Generate baseline simulation progression clock."""
        return Simulation(
            simulation_time=8.0,
            start_time=0.0,
            end_time=24.0,
            simulation_status=SimulationStatus.IDLE,
        )

    def generate_grid_baseline(self) -> Grid:
        """Generate baseline utility grid limit and available capacity."""
        configured = 150.0
        active = 150.0
        # Building demand 60kW - Solar 40kW = 20kW net grid import
        import_kw = 20.0
        available = active - import_kw
        return Grid(
            configured_limit_kw=configured,
            active_limit_kw=active,
            current_import_kw=import_kw,
            available_capacity_kw=available,
            safety_state=SafetyState.NORMAL,
            emergency_mode=False,
        )

    def generate_initial_system_state(self, ev_count: int = 8, station_count: int = 8) -> SystemState:
        """
        Generate complete canonical SystemState initialized for simulation start.
        Optionally connects initial EVs to stations in arrival order.
        """
        sim = self.generate_simulation_baseline()
        env = self.generate_environment_baseline()
        grid = self.generate_grid_baseline()
        building = self.generate_building_baseline()
        solar = self.generate_solar_baseline()
        stations = self.generate_stations(count=station_count)
        evs = self.generate_evs(count=ev_count)

        # In initial state before optimizer runs, no active allocations dispatched
        allocations = {s.station_id: 0.0 for s in stations}

        return SystemState(
            simulation=sim,
            environment=env,
            grid=grid,
            building=building,
            solar=solar,
            stations=stations,
            evs=evs,
            allocations=allocations,
            alerts=[],
            strategy="BALANCED",
            emergency=False,
        )

def generate_initial_fleet_and_stations(ev_count: int = 8, station_count: int = 6) -> SystemState:
    """
    Returns a pristine, deterministically generated initial system state, 
    complete with stations and a realistic mix of EVs.
    Used for live server boot and simulation resets.
    """
    generator = SyntheticDataGenerator(seed=42)
    return generator.generate_initial_system_state(ev_count=ev_count, station_count=station_count)
