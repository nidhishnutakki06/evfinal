import threading
from typing import Optional, Union, Dict, Any
from pydantic import ValidationError

from app.models.pydantic_state import (
    SystemState, Grid, Emergency, Station, EV, Allocation, Alert,
    Simulation, Environment, Building, Solar, Strategy
)
from app.services.repository import PersistenceRepository

class RuntimeStateManager:
    """
    The RuntimeStateManager is the authoritative owner of LIVE state.
    It holds the canonical SystemState in memory.
    """
    def __init__(self):
        # We use an RLock to provide safe state mutation boundaries.
        self._lock = threading.RLock()
        self._state: SystemState = self._create_initial_state()

    def _create_initial_state(self) -> SystemState:
        """
        Creates a deterministic empty initial state.
        It is structurally valid under the Phase 2 contracts.
        """
        return SystemState(
            grid=Grid(configured_limit=0.0, active_limit=0.0),
            emergency=Emergency(emergency_active_state=False, emergency_limit=0.0)
        )

    def get_state(self) -> SystemState:
        """
        Return the current state.
        Uses Pydantic's deep copy to ensure immutable safe access for callers.
        """
        with self._lock:
            return self._state.model_copy(deep=True)

    def replace_state(self, candidate_state: SystemState) -> bool:
        """
        Receives a candidate SystemState.
        Validates structural correctness fully.
        Rejects invalid state and preserves existing canonical state.
        Replaces the canonical state if accepted.
        Returns True if replaced, False if rejected.
        """
        with self._lock:
            try:
                # We dump and re-validate to ensure no nested objects bypass validation.
                valid_state = SystemState.model_validate(candidate_state.model_dump())
                self._state = valid_state
                return True
            except ValidationError:
                return False

    def create_reset_state(self) -> SystemState:
        """
        Generates a deterministic pristine state matching reset semantics,
        without applying it to canonical memory.
        """
        with self._lock:
            current_grid_configured_limit = self._state.grid.configured_limit
            current_emergency_limit = self._state.emergency.emergency_limit
            
            # Recreate base state
            new_state = self._create_initial_state()
            
            # Restore grid constraints
            new_state.grid.configured_limit = current_grid_configured_limit
            new_state.grid.active_limit = current_grid_configured_limit
            new_state.grid.available_capacity = current_grid_configured_limit
            
            # Restore emergency constraints
            new_state.emergency.emergency_limit = current_emergency_limit
            
            # Seed deterministic fleet and stations
            from src.sh305.synthetic.generator import generate_initial_fleet_and_stations
            from app.core.engine_boundary import EngineBoundary
            internal_state = generate_initial_fleet_and_stations()
            boundary = EngineBoundary()
            boundary.seed_fleet_to_pydantic(new_state, internal_state)
            
            return new_state

    def reset_state(self) -> None:
        """
        Deterministic reset behavior.
        """
        with self._lock:
            self._state = self.create_reset_state()

    def initialize_from_definitions(self, repo: PersistenceRepository) -> None:
        """
        Receives persisted definitions and maps them into Pydantic runtime state.
        This provides a clean mapping approach without making SystemState query the DB.
        """
        with self._lock:
            # 1. Initialize Stations
            db_stations = repo.get_all_station_definitions()
            self._state.stations = []
            for st_def in db_stations:
                st = Station(
                    station_id=st_def.station_id,
                    capacity=st_def.capacity,
                    minimum_charging_rate=st_def.minimum_charging_rate,
                    maximum_charging_rate=st_def.maximum_charging_rate,
                    # Runtime explicit defaults
                    occupancy=False,
                    connected_ev_id=None,
                    allocated_power=0.0,
                    status="AVAILABLE"
                )
                self._state.stations.append(st)
                
            # 2. Initialize EVs
            db_evs = repo.get_all_ev_definitions()
            self._state.evs = []
            for ev_def in db_evs:
                ev = EV(
                    ev_id=ev_def.id,
                    vehicle_type=ev_def.vehicle_type,
                    battery_capacity=ev_def.battery_capacity,
                    range=ev_def.range,
                    minimum_rate=ev_def.minimum_charging_rate,
                    maximum_rate=ev_def.maximum_charging_rate,
                    # Runtime explicit boundary - deterministic neutral defaults
                    current_soc=0.0,
                    target_soc=100.0,
                    requested_travel_distance=0.0,
                    arrival=0.0,
                    departure=0.0,
                    current_rate=0.0,
                    energy_required=0.0,
                    time_remaining=0.0,
                    required_average_power=0.0,
                    urgency="NORMAL",
                    priority_score=0.0,
                    estimated_completion=0.0,
                    estimated_soc_at_departure=0.0,
                    deadline_status="ON_TRACK",
                    physical_feasibility=True,
                    current_allocation_feasibility=True,
                    a3_risk="NONE",
                    a2_reason="INIT",
                    grid_contribution=0.0,
                    solar_contribution=0.0,
                    station_id=None
                )
                self._state.evs.append(ev)
                
            # 3. Initialize Scenario configurations (Optional based on repo data)
            db_scenarios = repo.get_all_scenario_profiles()
            # If a scenario profile exists, we don't automatically override grid limits 
            # here unless structured. We leave it neutral.
            pass
