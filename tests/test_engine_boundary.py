import pytest
from sh305.synthetic.generator import SyntheticDataGenerator
from sh305.integration.adapter import to_backend_state
from app.core.engine_boundary import EngineBoundary
import copy

@pytest.fixture
def base_candidate():
    # Generate a rich internal state and convert it to candidate dict
    generator = SyntheticDataGenerator(seed=42)
    state = generator.generate_initial_system_state()
    return to_backend_state(state)

def test_normal_engine_boundary_calculation(base_candidate):
    candidate = copy.deepcopy(base_candidate)
    result = EngineBoundary.calculate(candidate)
    
    assert "allocations" in result
    assert "evs" in result
    assert len(result["evs"]) > 0
    # Engine should compute current_rate and A2 reasons
    for ev in result["evs"]:
        assert ev["current_rate"] >= 0.0
        assert len(ev["a2_reason"]) > 0

def test_simulation_timestep_behavior(base_candidate):
    candidate = copy.deepcopy(base_candidate)
    candidate["simulation"]["is_running"] = True
    candidate["simulation"]["timestep"] = 0.25
    
    original_time = candidate["simulation"]["simulation_time"]
    
    result = EngineBoundary.calculate(candidate)
    
    assert result["simulation"]["simulation_time"] == original_time + 0.25

def test_strategy_changes(base_candidate):
    strategies = ["DEADLINE_FIRST", "SOLAR_FIRST", "GRID_SAFETY_FIRST"]
    for strategy in strategies:
        candidate = copy.deepcopy(base_candidate)
        candidate["strategy"]["active_strategy"] = strategy
        
        result = EngineBoundary.calculate(candidate)
        assert result["strategy"]["active_strategy"] == strategy

def test_emergency_toggle(base_candidate):
    candidate = copy.deepcopy(base_candidate)
    candidate["emergency"]["emergency_active_state"] = True
    candidate["emergency"]["emergency_limit"] = 0.40
    
    result = EngineBoundary.calculate(candidate)
    
    assert result["emergency"]["emergency_active_state"] is True
    # The grid limit in the candidate should be reduced
    assert result["grid"]["emergency_mode"] is True
    
    # Now restore
    result["emergency"]["emergency_active_state"] = False
    result_restored = EngineBoundary.calculate(result)
    
    assert result_restored["emergency"]["emergency_active_state"] is False
    assert result_restored["grid"]["emergency_mode"] is False

def test_deterministic_calculation(base_candidate):
    c1 = copy.deepcopy(base_candidate)
    c2 = copy.deepcopy(base_candidate)
    
    r1 = EngineBoundary.calculate(c1)
    r2 = EngineBoundary.calculate(c2)
    
    # Should yield exact same allocation
    alloc1 = {a["station_id"]: a["allocated_power"] for a in r1["allocations"]}
    alloc2 = {a["station_id"]: a["allocated_power"] for a in r2["allocations"]}
    
    assert alloc1 == alloc2
