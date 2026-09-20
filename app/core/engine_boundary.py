from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.models.pydantic_state import SystemState
from src.sh305.integration.adapter import from_backend_state, to_backend_state
from src.sh305.engine.controller import _recompute
from src.sh305.engine.simulation import step_simulation

class CalculationContext(BaseModel):
    """
    Input context provided to the engine boundary.
    Conceptually holds all necessary state to perform optimizations.
    """
    state: SystemState

class CalculationResult(BaseModel):
    """
    Result returned by the simulation/optimization engine.
    Carries the updated state dictionary to be merged back by the ControlService.
    """
    updated_state_dict: Optional[Dict[str, Any]] = None

class EngineBoundary:
    """
    Interface for the simulation/optimization engine.
    Calculates EV priorities, allocations, and grid math based on the provided context.
    Returns deterministic results to be assembled into the canonical state by the backend.
    """
    def _translate_to_internal(self, state: SystemState):
        from sh305.domain.system_state import SystemState as InternalSystemState
        from sh305.domain.simulation import Simulation
        from sh305.domain.environment import Environment, Solar
        from sh305.domain.grid import Grid
        from sh305.domain.building import Building
        from sh305.domain.station import Station as InternalStation
        from sh305.domain.ev import EV as InternalEV
        from sh305.domain.enums import (
            VehicleType, UserUrgency, WeatherCondition, TimeOfDay, 
            SafetyState, SimulationStatus, StationStatus, DeadlineStatus
        )
        from src.sh305.integration.adapter import VEHICLE_TYPE_MAPPING, URGENCY_MAPPING
        
        sim_status = "RUNNING" if state.simulation.is_running else "IDLE"
        internal_sim = Simulation(
            simulation_time=state.simulation.simulation_time,
            start_time=0.0,
            end_time=24.0,
            simulation_status=SimulationStatus(sim_status),
            timestep=state.simulation.timestep if hasattr(state.simulation, "timestep") else 0.25
        )
        
        internal_env = Environment(
            weather=WeatherCondition(state.environment.weather.upper()),
            time_of_day=TimeOfDay(state.environment.time_of_day.upper())
        )
        
        s_state = state.grid.safety_state.upper()
        if s_state == "SAFE":
            s_state = "NORMAL"
            
        emerg_active = state.emergency.emergency_active_state
        act_limit = max(0.001, state.grid.active_limit)
        if emerg_active:
            act_limit = max(0.001, state.grid.configured_limit * (1.0 - state.emergency.emergency_limit))
            
        internal_grid = Grid(
            configured_limit_kw=max(0.001, state.grid.configured_limit),
            active_limit_kw=max(0.001, act_limit),
            current_import_kw=state.grid.grid_import,
            available_capacity_kw=state.grid.available_capacity,
            safety_state=SafetyState(s_state),
            emergency_mode=emerg_active
        )
        
        internal_bld = Building(
            ac_demand_kw=state.building.ac_demand,
            lights_demand_kw=state.building.lights_demand,
            lifts_demand_kw=state.building.lifts_demand,
            appliances_demand_kw=state.building.appliances_demand,
            manual_demand_offset_kw=getattr(state.building, "manual_demand_offset", 0.0),
            total_demand_kw=state.building.total_building_demand
        )
        
        internal_sol = Solar(
            generation_kw=state.solar.generation
        )
        
        internal_stations = []
        ev_to_station = {}
        for st in state.stations:
            internal_stations.append(InternalStation(
                station_id=st.station_id,
                connected_ev_id=st.connected_ev_id,
                station_capacity_kw=st.capacity,
                min_charging_rate_kw=st.minimum_charging_rate,
                max_charging_rate_kw=st.maximum_charging_rate,
                occupied=st.occupancy,
                current_allocated_power_kw=st.allocated_power,
                status=StationStatus(st.status.upper()),
                grid_contribution_kw=0.0,
                renewable_contribution_kw=0.0
            ))
            if st.connected_ev_id:
                ev_to_station[st.connected_ev_id] = st.station_id
                
        internal_evs = []
        for ev in state.evs:
            v_type_str = ev.vehicle_type
            if v_type_str not in VEHICLE_TYPE_MAPPING:
                v_type_str = "Car"
            
            urgency_str = getattr(ev, "urgency", "NORMAL").upper()
            if urgency_str not in URGENCY_MAPPING:
                urgency_str = "NORMAL"
                
            internal_evs.append(InternalEV(
                ev_id=ev.ev_id,
                station_id=ev_to_station.get(ev.ev_id),
                vehicle_type=VEHICLE_TYPE_MAPPING[v_type_str],
                user_urgency=URGENCY_MAPPING[urgency_str],
                battery_capacity_kwh=ev.battery_capacity,
                expected_range_km=max(0.001, getattr(ev, "range", getattr(ev, "expected_range", 0.001))),
                current_soc=ev.current_soc,
                requested_travel_distance_km=getattr(ev, "requested_travel_distance", 0.0),
                arrival_time=ev.arrival,
                departure_time=ev.departure,
                min_charging_rate_kw=getattr(ev, "minimum_rate", 0.0),
                max_charging_rate_kw=ev.maximum_rate,
                current_charging_rate_kw=getattr(ev, "current_rate", 0.0),
                energy_required_kwh=getattr(ev, "energy_required", 0.0),
                time_remaining_hours=getattr(ev, "time_remaining", 0.0),
                required_average_power_kw=getattr(ev, "required_average_power", 0.0),
                priority_score=getattr(ev, "priority_score", 0.0),
                estimated_completion_time=getattr(ev, "estimated_completion", 0.0),
                estimated_soc_at_departure=getattr(ev, "estimated_soc_at_departure", 0.0),
                deadline_status=DeadlineStatus(getattr(ev, "deadline_status", "ON_TRACK").upper()),
                physical_feasibility=getattr(ev, "physical_feasibility", True),
                current_allocation_feasibility=getattr(ev, "current_allocation_feasibility", True),
                predictive_risk_flag=getattr(ev, "a3_risk", "NONE") != "NONE",
                reason=getattr(ev, "a2_reason", "INIT"),
                grid_contribution_kw=getattr(ev, "grid_contribution", 0.0),
                solar_contribution_kw=getattr(ev, "solar_contribution", 0.0)
            ))
            
        internal_state = InternalSystemState(
            simulation=internal_sim,
            environment=internal_env,
            grid=internal_grid,
            building=internal_bld,
            solar=internal_sol,
            stations=internal_stations,
            evs=internal_evs,
            strategy=state.strategy.active_strategy if hasattr(state, "strategy") else "BALANCED",
            emergency=state.emergency.emergency_active_state if hasattr(state, "emergency") else False,
            allocations={},
            alerts=[]
        )
        return internal_state

    def _translate_to_pydantic(self, state: SystemState, internal_state):
        # Map back directly into context.state to avoid Pydantic schema validation crashes
        state.simulation.simulation_time = internal_state.simulation.simulation_time
        state.environment.time_of_day = internal_state.environment.time_of_day.value.title()
        state.environment.weather = internal_state.environment.weather.value.title()
        
        state.building.ac_demand = internal_state.building.ac_demand_kw
        state.building.lights_demand = internal_state.building.lights_demand_kw
        state.building.lifts_demand = internal_state.building.lifts_demand_kw
        state.building.appliances_demand = internal_state.building.appliances_demand_kw
        if hasattr(state.building, "manual_demand_offset"):
            state.building.manual_demand_offset = internal_state.building.manual_demand_offset_kw
        state.building.total_building_demand = internal_state.building.total_demand_kw
        
        # Clean up floating point epsilon from 0.001 boundary limits
        if internal_state.grid.current_import_kw < 0.01:
            state.grid.grid_import = 0.0
        else:
            state.grid.grid_import = internal_state.grid.current_import_kw
            if state.grid.grid_import > state.grid.active_limit:
                state.grid.grid_import = state.grid.active_limit
                
        state.grid.available_capacity = internal_state.grid.available_capacity_kw
        state.solar.generation = internal_state.solar.generation_kw
        state.solar.usable_solar = internal_state.solar.usable_solar_kw
        state.solar.excess_solar = internal_state.solar.excess_solar_kw
        
        # Map stations
        st_map = {st.station_id: st for st in internal_state.stations}
        for st in state.stations:
            if st.station_id in st_map:
                ist = st_map[st.station_id]
                st.allocated_power = ist.current_allocated_power_kw if ist.current_allocated_power_kw >= 0.01 else 0.0
                st.status = ist.status.value
                st.connected_ev_id = ist.connected_ev_id
                st.occupancy = ist.occupied
                
        # Map EVs
        ev_map = {ev.ev_id: ev for ev in internal_state.evs}
        for ev in state.evs:
            if ev.ev_id in ev_map:
                iev = ev_map[ev.ev_id]
                ev.station_id = iev.station_id
                ev.current_soc = iev.current_soc
                if hasattr(ev, "current_rate"): ev.current_rate = iev.current_charging_rate_kw if iev.current_charging_rate_kw >= 0.01 else 0.0
                if hasattr(ev, "energy_required"): ev.energy_required = iev.energy_required_kwh
                if hasattr(ev, "time_remaining"): ev.time_remaining = max(0.0, iev.time_remaining_hours)
                if hasattr(ev, "required_average_power"): ev.required_average_power = iev.required_average_power_kw
                if hasattr(ev, "priority_score"): ev.priority_score = iev.priority_score
                if hasattr(ev, "estimated_completion"): ev.estimated_completion = iev.estimated_completion_time or 0.0
                if hasattr(ev, "estimated_soc_at_departure"): ev.estimated_soc_at_departure = iev.estimated_soc_at_departure or 0.0
                if hasattr(ev, "deadline_status"): ev.deadline_status = iev.deadline_status.value
                if hasattr(ev, "physical_feasibility"): ev.physical_feasibility = iev.physical_feasibility
                if hasattr(ev, "current_allocation_feasibility"): ev.current_allocation_feasibility = iev.current_allocation_feasibility
                if hasattr(ev, "a3_risk"): ev.a3_risk = "HIGH_RISK" if iev.predictive_risk_flag else "NONE"
                if hasattr(ev, "a2_reason"): ev.a2_reason = iev.reason
                if hasattr(ev, "grid_contribution"): ev.grid_contribution = iev.grid_contribution_kw
                if hasattr(ev, "solar_contribution"): ev.solar_contribution = iev.solar_contribution_kw

        # Map allocations
        if hasattr(state, "allocations"):
            from app.models.pydantic_state import Allocation as PydanticAllocation
            state.allocations.clear()
            for iev in internal_state.evs:
                if iev.station_id:
                    state.allocations.append(PydanticAllocation(
                        ev_id=iev.ev_id,
                        allocated_rate=iev.current_charging_rate_kw if iev.current_charging_rate_kw >= 0.01 else 0.0,
                        allocation_status="ACTIVE" if iev.current_charging_rate_kw > 0.01 else "PENDING",
                        grid_contribution=iev.grid_contribution_kw,
                        solar_contribution=iev.solar_contribution_kw
                    ))

    def seed_fleet_to_pydantic(self, state: SystemState, internal_state) -> None:
        from app.models.pydantic_state import Station as PydanticStation, EV as PydanticEV
        state.stations = []
        for ist in internal_state.stations:
            state.stations.append(PydanticStation(
                station_id=ist.station_id,
                capacity=ist.station_capacity_kw,
                minimum_charging_rate=ist.min_charging_rate_kw,
                maximum_charging_rate=ist.max_charging_rate_kw,
                occupancy=ist.occupied,
                connected_ev_id=ist.connected_ev_id,
                allocated_power=ist.current_allocated_power_kw,
                status=ist.status.value
            ))
            
        state.evs = []
        for iev in internal_state.evs:
            state.evs.append(PydanticEV(
                ev_id=iev.ev_id,
                vehicle_type=iev.vehicle_type.value,
                battery_capacity=iev.battery_capacity_kwh,
                range=iev.expected_range_km,
                minimum_rate=iev.min_charging_rate_kw,
                maximum_rate=iev.max_charging_rate_kw,
                current_soc=iev.current_soc,
                target_soc=iev.target_soc if iev.target_soc else 100.0,
                requested_travel_distance=iev.requested_travel_distance_km,
                arrival=iev.arrival_time,
                departure=iev.departure_time,
                current_rate=iev.current_charging_rate_kw,
                energy_required=iev.energy_required_kwh,
                time_remaining=max(0.0, iev.time_remaining_hours),
                required_average_power=iev.required_average_power_kw,
                urgency=iev.user_urgency.value,
                priority_score=iev.priority_score,
                estimated_completion=iev.estimated_completion_time or 0.0,
                estimated_soc_at_departure=iev.estimated_soc_at_departure or 0.0,
                deadline_status=iev.deadline_status.value if iev.deadline_status else "ON_TRACK",
                physical_feasibility=iev.physical_feasibility if iev.physical_feasibility is not None else True,
                current_allocation_feasibility=iev.current_allocation_feasibility if iev.current_allocation_feasibility is not None else True,
                a3_risk="HIGH_RISK" if iev.predictive_risk_flag else "NONE",
                a2_reason=iev.reason,
                grid_contribution=iev.grid_contribution_kw,
                solar_contribution=iev.solar_contribution_kw,
                station_id=iev.station_id
            ))

    def calculate(self, context: CalculationContext) -> CalculationResult:
        state = context.state
        
        # 1. Translate Pydantic to internal engine state
        internal_state = self._translate_to_internal(state)
        
        # 2. Execute Engine
        _recompute(internal_state)
        
        if state.simulation.is_running:
            internal_state.simulation.simulation_time += getattr(state.simulation, "timestep", 0.25)
            
        # 3. Map back directly into context.state
        self._translate_to_pydantic(state, internal_state)
        
        # Clear updated_state_dict since we mutate directly
        return CalculationResult()

    def step(self, context: CalculationContext) -> CalculationResult:
        state = context.state
        
        # 1. Translate Pydantic to internal engine state
        internal_state = self._translate_to_internal(state)
        
        # 2. Execute Engine simulation step
        timestep = getattr(state.simulation, "timestep", 0.25)
        step_simulation(internal_state, step_hours=timestep)
        
        # 3. Map back directly into context.state
        self._translate_to_pydantic(state, internal_state)
        
        return CalculationResult()
