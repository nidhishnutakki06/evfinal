from typing import Dict, Any, List, Optional
from app.services.state_manager import RuntimeStateManager
from app.core.engine_boundary import EngineBoundary, CalculationContext, CalculationResult
from app.services.validation import StateValidator
from app.models.pydantic_state import SystemState, EV

class ControlService:
    def __init__(self, state_manager: RuntimeStateManager, engine: EngineBoundary, validator: StateValidator):
        self.state_manager = state_manager
        self.engine = engine
        self.validator = validator

    def _merge_result(self, candidate: SystemState, result: CalculationResult) -> SystemState:
        # Applies optimization calculation results to the candidate state.
        return candidate

    def _orchestrate(self, candidate_state: SystemState) -> SystemState:
        # 1. Create context
        context = CalculationContext(state=candidate_state)
        # 2. Invoke engine boundary
        result = self.engine.calculate(context)
        # 3. Assemble result
        assembled_candidate = self._merge_result(candidate_state, result)
        # 4. Validate
        validation_result = self.validator.validate(assembled_candidate)
        if not validation_result.is_valid:
            raise ValueError(f"Candidate state rejected by validation invariants: {', '.join(validation_result.errors)}")
        # 5. Canonical replacement
        if not self.state_manager.replace_state(assembled_candidate):
            raise ValueError("Candidate state rejected by structural constraints.")
        
        return self.state_manager.get_state()

    def process_simulation_step(self) -> SystemState:
        candidate_state = self.state_manager.get_state()
        context = CalculationContext(state=candidate_state)
        result = self.engine.step(context)
        assembled_candidate = self._merge_result(candidate_state, result)
        validation_result = self.validator.validate(assembled_candidate)
        if not validation_result.is_valid:
            raise ValueError(f"Candidate state rejected by validation invariants: {', '.join(validation_result.errors)}")
        if not self.state_manager.replace_state(assembled_candidate):
            raise ValueError("Candidate state rejected by structural constraints.")
        return self.state_manager.get_state()

    def process_simulation_status(self, is_running: bool) -> SystemState:
        candidate = self.state_manager.get_state()
        candidate.simulation.is_running = is_running
        return self._orchestrate(candidate)

    def process_reset_simulation(self) -> SystemState:
        candidate = self.state_manager.create_reset_state()
        return self._orchestrate(candidate)

    def process_building_demand(self, ac: float, lights: float, lifts: float, appliances: float) -> SystemState:
        candidate = self.state_manager.get_state()
        candidate.building.ac_demand = ac
        candidate.building.lights_demand = lights
        candidate.building.lifts_demand = lifts
        candidate.building.appliances_demand = appliances
        candidate.building.total_building_demand = ac + lights + lifts + appliances
        return self._orchestrate(candidate)

    def process_grid_limit(self, limit: float) -> SystemState:
        candidate = self.state_manager.get_state()
        candidate.grid.configured_limit = limit
        if not candidate.emergency.emergency_active_state:
            candidate.grid.active_limit = limit
        return self._orchestrate(candidate)

    def process_weather(self, weather: str, time_of_day: Optional[str] = None) -> SystemState:
        candidate = self.state_manager.get_state()
        if weather:
            candidate.environment.weather = weather
        if time_of_day:
            candidate.environment.time_of_day = time_of_day
        return self._orchestrate(candidate)

    def process_spawn_ev(self, ev_data: Dict[str, Any], is_urgent: bool = False) -> SystemState:
        candidate = self.state_manager.get_state()
        if any(ev.ev_id == ev_data["ev_id"] for ev in candidate.evs):
            raise ValueError("EV with this ID already exists")
            
        station_id = ev_data.get("station_id")
        if station_id:
            # Validate and assign to station
            station = next((s for s in candidate.stations if s.station_id == station_id), None)
            if not station:
                raise ValueError("Station ID does not exist")
            if station.occupancy:
                raise ValueError("Station is already occupied")
            station.occupancy = True
            station.connected_ev_id = ev_data["ev_id"]
            
        new_ev = EV(
            ev_id=ev_data["ev_id"],
            vehicle_type=ev_data["vehicle_type"],
            battery_capacity=ev_data["battery_capacity"],
            range=0.0,
            current_soc=0.0,
            target_soc=ev_data["target_soc"],
            requested_travel_distance=ev_data.get("requested_travel_distance", 0.0),
            arrival=ev_data["arrival"],
            departure=ev_data["departure"],
            minimum_rate=ev_data.get("minimum_rate", 0.0),
            maximum_rate=ev_data["maximum_rate"],
            current_rate=0.0,
            energy_required=0.0,
            time_remaining=0.0,
            required_average_power=0.0,
            urgency="URGENT" if is_urgent else "NORMAL",
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
            station_id=station_id
        )
        candidate.evs.append(new_ev)
        return self._orchestrate(candidate)

    def process_strategy(self, active_strategy: str) -> SystemState:
        candidate = self.state_manager.get_state()
        candidate.strategy.active_strategy = active_strategy
        return self._orchestrate(candidate)

    def process_emergency_activation(self, activate: bool) -> SystemState:
        candidate = self.state_manager.get_state()
        candidate.emergency.emergency_active_state = activate
        if activate:
            candidate.grid.active_limit = candidate.emergency.emergency_limit
        else:
            candidate.grid.active_limit = candidate.grid.configured_limit
        return self._orchestrate(candidate)
