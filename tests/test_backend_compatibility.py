import pytest
from sh305.synthetic.generator import SyntheticDataGenerator
from sh305.integration.adapter import to_backend_state, from_backend_state
from sh305.engine.controller import _recompute

def test_adapter_backend_compatibility():
    # 1. Generate engine state
    generator = SyntheticDataGenerator(seed=1)
    state = generator.generate_initial_system_state()
    
    # 2. Run initial recompute to populate all fields
    _recompute(state)
    
    # 3. Translate engine results to backend-compatible result data
    backend_dict = to_backend_state(state)
    
    # Verify structure matches backend expectations
    assert "simulation" in backend_dict
    assert "strategy" in backend_dict
    assert "emergency" in backend_dict
    assert "building" in backend_dict
    assert isinstance(backend_dict["allocations"], list)
    
    # Verify internal fields are mapped correctly
    ev_data = backend_dict["evs"][0]
    assert "battery_capacity" in ev_data
    assert "range" in ev_data
    assert "current_soc" in ev_data
    assert "minimum_rate" in ev_data
    assert "maximum_rate" in ev_data
    assert "current_rate" in ev_data
    assert "energy_required" in ev_data
    assert "time_remaining" in ev_data
    assert "required_average_power" in ev_data
    assert "estimated_completion" in ev_data
    assert "a3_risk" in ev_data
    assert "a2_reason" in ev_data

    # Test reverse mapping
    # 4. Modify backend dictionary (simulating external API input)
    backend_dict["strategy"]["active_strategy"] = "SOLAR_FIRST"
    backend_dict["building"]["appliances_demand"] = 80.0
    
    # 5. Translate backend state -> engine inputs
    state = from_backend_state(backend_dict)
    
    # Verify engine state was correctly mutated
    assert state.strategy == "SOLAR_FIRST"
    assert state.building.appliances_demand_kw == 80.0
    
    # 6. Check that engine calculation continues running without errors
    _recompute(state)
    assert state.strategy == "SOLAR_FIRST" # ensure it stayed consistent

def test_unmapped_semantics_fail():
    generator = SyntheticDataGenerator(seed=1)
    state = generator.generate_initial_system_state()
    backend_dict = to_backend_state(state)
    
    # Create invalid semantic inputs
    backend_dict["evs"][0]["vehicle_type"] = "TRUCK" # Unmapped
    
    with pytest.raises(ValueError, match="Unmapped semantic value for vehicle_type: TRUCK"):
        from_backend_state(backend_dict)

    backend_dict["evs"][0]["vehicle_type"] = "Car"
    backend_dict["evs"][0]["urgency"] = "SUPER_URGENT" # Unmapped
    
    with pytest.raises(ValueError, match="Unmapped semantic value for urgency: SUPER_URGENT"):
        from_backend_state(backend_dict)

def test_lossy_vehicle_mapping():
    from sh305.domain.enums import VehicleType
    generator = SyntheticDataGenerator(seed=1)
    state = generator.generate_initial_system_state()
    
    # 1. Manually set EV to SUV (which maps to Car)
    state.evs[0].vehicle_type = VehicleType.SUV
    
    # 2. Translate to backend
    backend_dict = to_backend_state(state)
    assert backend_dict["evs"][0]["vehicle_type"] == "Car"
    
    # 3. Translate back
    state_restored = from_backend_state(backend_dict)
    
    # 4. Proves the mapping is lossy; it came back as SEDAN, not SUV
    assert state_restored.evs[0].vehicle_type == VehicleType.SEDAN
    assert state_restored.evs[0].vehicle_type != VehicleType.SUV
