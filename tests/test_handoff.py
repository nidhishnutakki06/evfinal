import pytest
from sh305.synthetic.generator import SyntheticDataGenerator
from sh305.engine.controller import set_strategy

def test_external_caller_handoff_flow():
    """
    Verifies that an external caller can successfully invoke an engine function
    and receive an updated canonical SystemState that cleanly serializes.
    """
    # 1. External caller initializes state (Person 3's generator or backend DB reconstructs it)
    generator = SyntheticDataGenerator(seed=123)
    state = generator.generate_initial_system_state()
    
    # Verify initial state baseline
    assert state.strategy == "BALANCED"
    
    # 2. External caller invokes an engine function
    set_strategy(state, "SOLAR_FIRST")
    
    # 3. Canonical SystemState is updated successfully
    assert state.strategy == "SOLAR_FIRST"
    assert len(state.evs) == 8
    
    # 4. Serialize to simulate handoff boundary (e.g. over REST or WebSocket)
    serialized_json = state.model_dump_json()
    assert isinstance(serialized_json, str)
    assert len(serialized_json) > 1000
    assert "SOLAR_FIRST" in serialized_json
