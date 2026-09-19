import pytest
import copy
from sh305.synthetic.generator import SyntheticDataGenerator
from sh305.integration.adapter import to_backend_state
from app.core.engine_boundary import EngineBoundary, CalculationContext, CalculationResult
from app.models.pydantic_state import SystemState

@pytest.fixture
def base_candidate():
    # Generate a rich internal state and convert it to candidate dict
    generator = SyntheticDataGenerator(seed=42)
    state = generator.generate_initial_system_state()
    state.strategy = "DEADLINE_FIRST"
    return to_backend_state(state)

def test_engine_boundary_returns_result():
    boundary = EngineBoundary()
    # Provide enough default fields so validation doesn't crash if needed
    state = SystemState(
        grid={"configured_limit": 100.0, "active_limit": 100.0}, 
        emergency={"emergency_limit": 50.0},
        building={"ac_demand": 0.0, "lights_demand": 0.0, "lifts_demand": 0.0, "appliances_demand": 0.0, "total_building_demand": 0.0},
        environment={"weather": "SUNNY", "temperature_c": 20.0, "time_of_day": "MORNING"},
        solar={"generation": 0.0, "usable_solar": 0.0, "excess_solar": 0.0},
        strategy={"active_strategy": "DEADLINE_FIRST"}
    )
    context = CalculationContext(state=state)
    
    result = boundary.calculate(context)
    
    assert isinstance(result, CalculationResult)

def test_normal_engine_boundary_calculation(base_candidate):
    boundary = EngineBoundary()
    candidate = copy.deepcopy(base_candidate)
    state = SystemState.model_validate(candidate)
    context = CalculationContext(state=state)
    boundary.calculate(context)
    
    res_dict = context.state.model_dump(mode='json')
    assert "allocations" in res_dict
    assert "evs" in res_dict
    assert len(res_dict["evs"]) > 0
    # Engine should compute current_rate and A2 reasons
    for ev in res_dict["evs"]:
        assert ev["current_rate"] >= 0.0
        assert len(ev["a2_reason"]) > 0

def test_simulation_timestep_behavior(base_candidate):
    boundary = EngineBoundary()
    candidate = copy.deepcopy(base_candidate)
    candidate["simulation"]["is_running"] = True
    candidate["simulation"]["timestep"] = 0.25
    
    original_time = candidate["simulation"]["simulation_time"]
    
    state = SystemState.model_validate(candidate)
    context = CalculationContext(state=state)
    boundary.calculate(context)
    
    res_dict = context.state.model_dump(mode='json')
    assert res_dict["simulation"]["simulation_time"] == original_time + 0.25

def test_strategy_changes(base_candidate):
    boundary = EngineBoundary()
    strategies = ["DEADLINE_FIRST", "SOLAR_FIRST", "GRID_SAFETY_FIRST"]
    for strategy in strategies:
        candidate = copy.deepcopy(base_candidate)
        candidate["strategy"]["active_strategy"] = strategy
        
        state = SystemState.model_validate(candidate)
        context = CalculationContext(state=state)
        boundary.calculate(context)
        
        res_dict = context.state.model_dump(mode='json')
        assert res_dict["strategy"]["active_strategy"] == strategy

def test_emergency_toggle(base_candidate):
    boundary = EngineBoundary()
    candidate = copy.deepcopy(base_candidate)
    candidate["emergency"]["emergency_active_state"] = True
    candidate["emergency"]["emergency_limit"] = 0.40
    
    state = SystemState.model_validate(candidate)
    context = CalculationContext(state=state)
    boundary.calculate(context)
    
    res_dict = context.state.model_dump(mode='json')
    assert res_dict["emergency"]["emergency_active_state"] is True
    assert res_dict["emergency"]["emergency_active_state"] is True
    
    # Now restore
    res_dict["emergency"]["emergency_active_state"] = False
    state_restored = SystemState.model_validate(res_dict)
    context_restored = CalculationContext(state=state_restored)
    boundary.calculate(context_restored)
    
    res_dict_restored = context_restored.state.model_dump(mode='json')
    assert res_dict_restored["emergency"]["emergency_active_state"] is False
    assert res_dict_restored["emergency"]["emergency_active_state"] is False

def test_deterministic_calculation(base_candidate):
    boundary = EngineBoundary()
    c1 = copy.deepcopy(base_candidate)
    c2 = copy.deepcopy(base_candidate)
    
    s1 = SystemState.model_validate(c1)
    s2 = SystemState.model_validate(c2)
    
    c_ctx1 = CalculationContext(state=s1)
    c_ctx2 = CalculationContext(state=s2)
    boundary.calculate(c_ctx1)
    boundary.calculate(c_ctx2)
    
    res_dict1 = c_ctx1.state.model_dump(mode='json')
    res_dict2 = c_ctx2.state.model_dump(mode='json')
    
    # Should yield exact same allocation
    alloc1 = {a["station_id"]: a["allocated_power"] for a in res_dict1["allocations"]}
    alloc2 = {a["station_id"]: a["allocated_power"] for a in res_dict2["allocations"]}
    
    assert alloc1 == alloc2
