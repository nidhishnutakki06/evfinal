from typing import Dict, Any, List
from sh305.domain.system_state import SystemState
from sh305.domain.simulation import Simulation
from sh305.domain.environment import Environment, Solar
from sh305.domain.grid import Grid
from sh305.domain.building import Building
from sh305.domain.station import Station
from sh305.domain.ev import EV
from sh305.domain.enums import (
    VehicleType, UserUrgency, WeatherCondition, TimeOfDay, 
    SafetyState, SimulationStatus, StationStatus, DeadlineStatus
)

# Explicit configurable semantic mappings
VEHICLE_TYPE_MAPPING = {
    "Car": VehicleType.SEDAN, # Default configurable mapping for Car
    "Scooter": VehicleType.SCOOTER,
    "Bike": VehicleType.BIKE,
}
REVERSE_VEHICLE_TYPE_MAPPING = {
    VehicleType.SUV: "Car",
    VehicleType.SEDAN: "Car",
    VehicleType.HATCHBACK: "Car",
    VehicleType.SCOOTER: "Scooter",
    VehicleType.BIKE: "Bike",
}

URGENCY_MAPPING = {
    "NORMAL": UserUrgency.MEDIUM,
    "URGENT": UserUrgency.CRITICAL,
}
REVERSE_URGENCY_MAPPING = {
    UserUrgency.LOW: "NORMAL",
    UserUrgency.MEDIUM: "NORMAL",
    UserUrgency.HIGH: "URGENT",
    UserUrgency.CRITICAL: "URGENT",
}

def to_backend_state(state: SystemState) -> Dict[str, Any]:
    """
    Translates internal Person 3 calculation engine SystemState 
    to the external Backend canonical SystemState representation.
    """
    backend_dict = {}

    # 1. Simulation
    backend_dict["simulation"] = {
        "simulation_time": state.simulation.simulation_time,
        "is_running": state.simulation.simulation_status == SimulationStatus.RUNNING,
        "timestep": 0.25, # Default, not inherently stored in state
        "start": state.simulation.start_time,
        "end": state.simulation.end_time,
        "status": state.simulation.simulation_status.value
    }
    
    # 2. Strategy & Emergency
    backend_dict["strategy"] = {
        "active_strategy": state.strategy
    }
    backend_dict["emergency"] = {
        "emergency_active_state": state.emergency,
        "emergency_limit": 0.40 # Default limit if active
    }
    
    # 3. Building
    # Treat total_building_demand as derived
    total_demand = (
        state.building.ac_demand_kw + 
        state.building.lights_demand_kw + 
        state.building.lifts_demand_kw + 
        state.building.appliances_demand_kw
    )
    backend_dict["building"] = {
        "ac_demand": state.building.ac_demand_kw,
        "lights_demand": state.building.lights_demand_kw,
        "lifts_demand": state.building.lifts_demand_kw,
        "appliances_demand": state.building.appliances_demand_kw,
        "total_building_demand": total_demand
    }
    
    # 4. Grid, Environment, Solar
    backend_dict["grid"] = {
        "configured_limit_kw": state.grid.configured_limit_kw,
        "active_limit_kw": state.grid.active_limit_kw,
        "current_import_kw": state.grid.current_import_kw,
        "available_capacity_kw": state.grid.available_capacity_kw,
        "safety_state": state.grid.safety_state.value,
        "emergency_mode": state.grid.emergency_mode
    }
    
    backend_dict["environment"] = {
        "weather": state.environment.weather.value,
        "time_of_day": state.environment.time_of_day.value
    }
    
    backend_dict["solar"] = {
        "generation_kw": state.solar.generation_kw
    }
    
    # 5. Stations
    backend_stations = []
    for st in state.stations:
        st_dict = {
            "station_id": st.station_id,
            "connected_ev_id": st.connected_ev_id,
            "station_capacity_kw": st.station_capacity_kw,
            "min_charging_rate_kw": st.min_charging_rate_kw,
            "max_charging_rate_kw": st.max_charging_rate_kw,
            "occupied": st.occupied,
            "current_allocated_power_kw": st.current_allocated_power_kw,
            "status": st.status.value,
            "grid_contribution_kw": st.grid_contribution_kw,
            "renewable_contribution_kw": st.renewable_contribution_kw
        }
        backend_stations.append(st_dict)
    backend_dict["stations"] = backend_stations

    # 6. Allocations (Array)
    allocations_list = []
    for st in state.stations:
        allocations_list.append({
            "station_id": st.station_id,
            "allocated_power": st.current_allocated_power_kw
        })
    backend_dict["allocations"] = allocations_list
    
    # 7. EVs
    backend_evs = []
    for ev in state.evs:
        ev_dict = {
            "ev_id": ev.ev_id,
            "vehicle_type": REVERSE_VEHICLE_TYPE_MAPPING.get(ev.vehicle_type, "Car"),
            "urgency": REVERSE_URGENCY_MAPPING.get(ev.user_urgency, "NORMAL"),
            "battery_capacity": ev.battery_capacity_kwh,
            "range": ev.expected_range_km,
            "current_soc": ev.current_soc,
            "requested_travel_distance": ev.requested_travel_distance_km,
            "arrival": ev.arrival_time,
            "departure": ev.departure_time,
            "minimum_rate": ev.min_charging_rate_kw,
            "maximum_rate": ev.max_charging_rate_kw,
            "current_rate": ev.current_charging_rate_kw,
            "energy_required": ev.energy_required_kwh,
            "time_remaining": ev.time_remaining_hours,
            "required_average_power": ev.required_average_power_kw,
            "estimated_completion": ev.estimated_completion_time,
            "a3_risk": ev.predictive_risk_flag,
            "a2_reason": ev.reason
        }
        backend_evs.append(ev_dict)
    backend_dict["evs"] = backend_evs

    # 8. Alerts
    backend_dict["alerts"] = state.alerts.copy()

    return backend_dict

def from_backend_state(backend_dict: Dict[str, Any]) -> SystemState:
    """
    Translates backend canonical state into a brand new internal engine SystemState.
    """
    sim_dict = backend_dict.get("simulation", {})
    sim_status_str = sim_dict.get("status", "IDLE")
    is_running = sim_dict.get("is_running", False)
    if is_running:
        sim_status_str = "RUNNING"

    simulation = Simulation(
        simulation_time=sim_dict.get("simulation_time", 0.0),
        start_time=sim_dict.get("start", 0.0),
        end_time=sim_dict.get("end", 24.0),
        simulation_status=SimulationStatus(sim_status_str)
    )

    env_dict = backend_dict.get("environment", {})
    environment = Environment(
        weather=WeatherCondition(env_dict.get("weather", "SUNNY")),
        time_of_day=TimeOfDay(env_dict.get("time_of_day", "MORNING"))
    )

    grid_dict = backend_dict.get("grid", {})
    grid = Grid(
        configured_limit_kw=grid_dict.get("configured_limit_kw", 150.0),
        active_limit_kw=grid_dict.get("active_limit_kw", 150.0),
        current_import_kw=grid_dict.get("current_import_kw", 0.0),
        available_capacity_kw=grid_dict.get("available_capacity_kw", 150.0),
        safety_state=SafetyState(grid_dict.get("safety_state", "NORMAL")),
        emergency_mode=grid_dict.get("emergency_mode", False)
    )

    bld_dict = backend_dict.get("building", {})
    ac = bld_dict.get("ac_demand", 0.0)
    lights = bld_dict.get("lights_demand", 0.0)
    lifts = bld_dict.get("lifts_demand", 0.0)
    apps = bld_dict.get("appliances_demand", 0.0)
    # total_building_demand is derived
    building = Building(
        ac_demand_kw=ac,
        lights_demand_kw=lights,
        lifts_demand_kw=lifts,
        appliances_demand_kw=apps,
        total_demand_kw=ac + lights + lifts + apps
    )

    sol_dict = backend_dict.get("solar", {})
    solar = Solar(
        generation_kw=sol_dict.get("generation_kw", 0.0)
    )

    stations = []
    for st_dict in backend_dict.get("stations", []):
        stations.append(Station(
            station_id=st_dict.get("station_id"),
            connected_ev_id=st_dict.get("connected_ev_id"),
            station_capacity_kw=st_dict.get("station_capacity_kw", 0.0),
            min_charging_rate_kw=st_dict.get("min_charging_rate_kw", 0.0),
            max_charging_rate_kw=st_dict.get("max_charging_rate_kw", 0.0),
            occupied=st_dict.get("occupied", False),
            current_allocated_power_kw=st_dict.get("current_allocated_power_kw", 0.0),
            status=StationStatus(st_dict.get("status", "AVAILABLE")),
            grid_contribution_kw=st_dict.get("grid_contribution_kw", 0.0),
            renewable_contribution_kw=st_dict.get("renewable_contribution_kw", 0.0)
        ))

    ev_to_station = {}
    for st in stations:
        if st.connected_ev_id:
            ev_to_station[st.connected_ev_id] = st.station_id

    evs = []
    for backend_ev in backend_dict.get("evs", []):
        v_type_str = backend_ev.get("vehicle_type", "Car")
        if v_type_str not in VEHICLE_TYPE_MAPPING:
            raise ValueError(f"Unmapped semantic value for vehicle_type: {v_type_str}")
        
        urgency_str = backend_ev.get("urgency", "NORMAL")
        if urgency_str not in URGENCY_MAPPING:
            raise ValueError(f"Unmapped semantic value for urgency: {urgency_str}")
            
        ev_id = backend_ev.get("ev_id")
        evs.append(EV(
            ev_id=ev_id,
            station_id=ev_to_station.get(ev_id),
            vehicle_type=VEHICLE_TYPE_MAPPING[v_type_str],
            user_urgency=URGENCY_MAPPING[urgency_str],
            battery_capacity_kwh=backend_ev.get("battery_capacity", 0.0),
            expected_range_km=backend_ev.get("range", 0.0),
            current_soc=backend_ev.get("current_soc", 0.0),
            requested_travel_distance_km=backend_ev.get("requested_travel_distance", 0.0),
            arrival_time=backend_ev.get("arrival", 0.0),
            departure_time=backend_ev.get("departure", 0.0),
            min_charging_rate_kw=backend_ev.get("minimum_rate", 0.0),
            max_charging_rate_kw=backend_ev.get("maximum_rate", 0.0),
            current_charging_rate_kw=backend_ev.get("current_rate", 0.0),
            energy_required_kwh=backend_ev.get("energy_required", 0.0),
            time_remaining_hours=backend_ev.get("time_remaining", 0.0),
            required_average_power_kw=backend_ev.get("required_average_power", 0.0),
            estimated_completion_time=backend_ev.get("estimated_completion"),
            predictive_risk_flag=backend_ev.get("a3_risk", False),
            reason=backend_ev.get("a2_reason", "")
        ))

    allocations = {}
    for alloc in backend_dict.get("allocations", []):
        allocations[alloc["station_id"]] = alloc["allocated_power"]

    strat_dict = backend_dict.get("strategy", {})
    strategy = strat_dict.get("active_strategy", "BALANCED")

    emg_dict = backend_dict.get("emergency", {})
    emergency = emg_dict.get("emergency_active_state", False)
    
    alerts = backend_dict.get("alerts", [])

    return SystemState(
        simulation=simulation,
        environment=environment,
        grid=grid,
        building=building,
        solar=solar,
        stations=stations,
        evs=evs,
        allocations=allocations,
        alerts=alerts,
        strategy=strategy,
        emergency=emergency
    )
