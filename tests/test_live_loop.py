import pytest
from app.models.pydantic_state import SystemState, Simulation, Environment, Grid, Building, Solar, Station, EV, Strategy, Emergency
from app.services.state_manager import RuntimeStateManager
from app.core.engine_boundary import EngineBoundary
from app.services.validation import StateValidator
from app.services.control import ControlService
from src.sh305.domain.enums import WeatherCondition

@pytest.fixture
def base_state():
    return SystemState(
        simulation=Simulation(simulation_time=8.0, is_running=True, timestep=1.0),
        environment=Environment(weather="Sunny", time_of_day="Morning"),
        grid=Grid(configured_limit=100.0, active_limit=100.0, grid_import=0.0, available_capacity=100.0, safety_state="SAFE"),
        building=Building(ac_demand=0.0, lights_demand=0.0, lifts_demand=0.0, appliances_demand=0.0, manual_demand_offset=0.0, total_building_demand=0.0),
        solar=Solar(generation=0.0, usable_solar=0.0, excess_solar=0.0),
        stations=[
            Station(station_id="ST-1", capacity=22.0, minimum_charging_rate=0.0, maximum_charging_rate=22.0, allocated_power=0.0, status="AVAILABLE")
        ],
        evs=[
            EV(
                ev_id="EV-1",
                vehicle_type="Car",
                battery_capacity=50.0,
                range=200.0,
                current_soc=20.0,
                target_soc=80.0,
                requested_travel_distance=100.0,
                arrival=10.0,
                departure=18.0,
                minimum_rate=0.0,
                maximum_rate=11.0,
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
        ],
        allocations=[],
        alerts=[],
        strategy=Strategy(active_strategy="DEADLINE_FIRST"),
        emergency=Emergency(emergency_active_state=False, emergency_limit=0.0)
    )

@pytest.fixture
def control_service(base_state):
    state_manager = RuntimeStateManager()
    state_manager.replace_state(base_state)
    engine = EngineBoundary()
    validator = StateValidator()
    return ControlService(state_manager, engine, validator)

def test_live_loop_simulation_time_and_solar(control_service):
    # Test a. Running N simulated steps advances simulation_time, changes time_of_day and produces solar.
    state = control_service.state_manager.get_state()
    assert state.simulation.simulation_time == 8.0
    
    # Step forward 1 hour (timestep=1.0)
    new_state = control_service.process_simulation_step()
    assert new_state.simulation.simulation_time == 9.0
    assert new_state.environment.time_of_day == "Morning"
    assert new_state.solar.generation > 0.0
    
    # Fast forward to night
    for _ in range(12):
        new_state = control_service.process_simulation_step()
        
    assert new_state.simulation.simulation_time == 21.0
    assert new_state.environment.time_of_day == "Night"
    assert new_state.solar.generation == 0.0

def test_live_loop_ev_arrival_departure(control_service):
    # Test b. An EV with arrival_time in the future is not connected to a station before that time.
    state = control_service.state_manager.get_state()
    assert state.simulation.simulation_time == 8.0
    ev = state.evs[0]
    assert ev.arrival == 10.0
    assert ev.station_id is None
    
    new_state = control_service.process_simulation_step() # 9.0
    assert new_state.evs[0].station_id is None
    
    new_state = control_service.process_simulation_step() # 10.0 (Arrival)
    assert new_state.evs[0].station_id == "ST-1"
    assert new_state.stations[0].occupancy is True
    
    # Fast forward to departure (18.0)
    for _ in range(8):
        new_state = control_service.process_simulation_step()
        
    assert new_state.simulation.simulation_time == 18.0
    assert new_state.evs[0].station_id is None
    assert new_state.stations[0].occupancy is False

def test_live_loop_manual_building_demand_persists(control_service):
    # Test c. An A1 building-demand delta applied is still reflected in total_demand_kw after several ticks
    
    # Add manual demand via control service
    # Wait, the controller function is apply_building_demand_delta
    # Let's use it directly or via a new control_service method if added.
    # Currently control_service has process_building_demand but it overwrites.
    # Let's test the controller function on the internal boundary or we can test it directly.
    # The requirement is that manual_demand_offset persists through process_simulation_step.
    state = control_service.state_manager.get_state()
    state.building.manual_demand_offset = 25.0
    control_service.state_manager.replace_state(state)
    
    new_state = control_service.process_simulation_step()
    
    # Total demand should be scheduled demand + 25.0
    # At 9.0 (Morning): lights=2.0, ac=5.0, lifts=15.0, appliances=10.0 => 32.0
    # + 25.0 = 57.0
    assert new_state.building.manual_demand_offset == 25.0
    assert new_state.building.total_building_demand == 57.0
    
    # One more step
    new_state = control_service.process_simulation_step()
    assert new_state.building.manual_demand_offset == 25.0
    assert new_state.building.total_building_demand == 57.0

def test_live_loop_weather_persists(control_service):
    # Test d. A weather change via change_weather() persists across several subsequent ticks.
    new_state = control_service.process_weather(weather="Rain")
    assert new_state.environment.weather == "Rain"
    
    # Step simulation
    for _ in range(3):
        new_state = control_service.process_simulation_step()
        
    assert new_state.environment.weather == "Rain"
