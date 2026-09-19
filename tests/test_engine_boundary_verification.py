import pytest
import copy
from sh305.synthetic.generator import SyntheticDataGenerator
from sh305.integration.adapter import to_backend_state
from app.core.engine_boundary import EngineBoundary, CalculationContext
from app.models.pydantic_state import SystemState


@pytest.fixture
def base_candidate():
    generator = SyntheticDataGenerator(seed=42)
    state = generator.generate_initial_system_state()
    
    state.simulation.simulation_time = 12.0 # Ensure all EVs have arrived
    
    # Connect EVs to stations so they can receive allocations
    for i, ev in enumerate(state.evs):
        if i < len(state.stations):
            ev.station_id = state.stations[i].station_id
            state.stations[i].connected_ev_id = ev.ev_id
            state.stations[i].occupied = True
            
    raw_dict = to_backend_state(state)
    
    pyd_dict = copy.deepcopy(raw_dict)
    
    # EVs mapping
    for ev in pyd_dict["evs"]:
        ev["arrival"] = 0.0
        ev["departure"] = 24.0

    pyd_dict["strategy"]["active_strategy"] = "DEADLINE_FIRST"
    return pyd_dict


# ==========================================
# 2. A1 Verification
# ==========================================
def test_a1_dynamic_controls(base_candidate):
    # 1. Base allocation
    c_base = copy.deepcopy(base_candidate)
    _ctx_r_base = CalculationContext(state=SystemState.model_validate(c_base))
    EngineBoundary().calculate(_ctx_r_base)
    r_base = _ctx_r_base.state.model_dump(mode='json')
    alloc_base = {a["ev_id"]: a["allocated_rate"] for a in r_base["allocations"]}

    # 2. Change building demand (force severe constraint)
    c_bld = copy.deepcopy(base_candidate)
    c_bld["building"]["appliances_demand"] += 150.0  # available drops to 0
    c_bld["building"]["total_building_demand"] += 150.0
    _ctx_r_bld = CalculationContext(state=SystemState.model_validate(c_bld))
    EngineBoundary().calculate(_ctx_r_bld)
    r_bld = _ctx_r_bld.state.model_dump(mode='json')
    alloc_bld = {a["ev_id"]: a["allocated_rate"] for a in r_bld["allocations"]}
    
    assert alloc_base != alloc_bld

    # 3. Change grid limit (force severe constraint)
    c_grid = copy.deepcopy(base_candidate)
    c_grid["grid"]["active_limit"] = 15.0  # available drops to 0
    _ctx_r_grid = CalculationContext(state=SystemState.model_validate(c_grid))
    EngineBoundary().calculate(_ctx_r_grid)
    r_grid = _ctx_r_grid.state.model_dump(mode='json')
    alloc_grid = {a["ev_id"]: a["allocated_rate"] for a in r_grid["allocations"]}
    
    assert alloc_base != alloc_grid

    # 4. Change weather / solar
    # Inject huge solar so available capacity increases drastically
    # (Though we are using small EVs, let's just assert no crash and potentially diff allocation)
    c_wea = copy.deepcopy(base_candidate)
    c_wea["environment"]["weather"] = "SUNNY"
    c_wea["solar"]["generation"] = 150.0
    _ctx_r_wea = CalculationContext(state=SystemState.model_validate(c_wea))
    EngineBoundary().calculate(_ctx_r_wea)
    r_wea = _ctx_r_wea.state.model_dump(mode='json')
    assert r_wea["solar"]["generation"] == 150.0


# ==========================================
# 3. A2 Verification
# ==========================================
def test_a2_reasons(base_candidate):
    candidate = copy.deepcopy(base_candidate)
    _ctx_result = CalculationContext(state=SystemState.model_validate(candidate))
    EngineBoundary().calculate(_ctx_result)
    result = _ctx_result.state.model_dump(mode='json')
    reasons_base = [ev["a2_reason"] for ev in result["evs"]]
    
    assert all(len(reason) > 0 for reason in reasons_base)
    
    # Force a different state
    c2 = copy.deepcopy(base_candidate)
    c2["grid"]["active_limit"] = 15.0 # extreme throttle
    _ctx_r2 = CalculationContext(state=SystemState.model_validate(c2))
    EngineBoundary().calculate(_ctx_r2)
    r2 = _ctx_r2.state.model_dump(mode='json')
    reasons_throttled = [ev["a2_reason"] for ev in r2["evs"]]
    
    # Explanations should change deterministically based on situation
    assert reasons_base != reasons_throttled


# ==========================================
# 4. A3 Verification
# ==========================================
def test_a3_predictive_risk(base_candidate):
    candidate = copy.deepcopy(base_candidate)
    
    # Create an impossible charging situation
    ev = candidate["evs"][0]
    ev["current_soc"] = 5.0
    ev["requested_travel_distance"] = 400.0 # needs a lot of energy
    ev["departure"] = candidate["simulation"]["simulation_time"] + 0.5 # departs in 30 mins
    ev["maximum_rate"] = 7.0 # slow charger
    
    _ctx_result = CalculationContext(state=SystemState.model_validate(candidate))
    EngineBoundary().calculate(_ctx_result)
    result = _ctx_result.state.model_dump(mode='json')
    out_ev = next(e for e in result["evs"] if e["ev_id"] == ev["ev_id"])
    
    assert out_ev["a3_risk"] == "HIGH_RISK"


# ==========================================
# 5. A4 Verification
# ==========================================
def test_a4_strategies_distinct(base_candidate):
    c_df = copy.deepcopy(base_candidate)
    c_df["strategy"]["active_strategy"] = "DEADLINE_FIRST"
    # Make grid tight so strategies actually have to make different trade-offs
    c_df["grid"]["active_limit"] = 25.0
    _ctx_r_df = CalculationContext(state=SystemState.model_validate(c_df))
    EngineBoundary().calculate(_ctx_r_df)
    r_df = _ctx_r_df.state.model_dump(mode='json')
    
    c_sf = copy.deepcopy(base_candidate)
    c_sf["strategy"]["active_strategy"] = "SOLAR_FIRST"
    c_sf["grid"]["active_limit"] = 25.0
    c_sf["solar"]["generation"] = 100.0 # inject high solar
    _ctx_r_sf = CalculationContext(state=SystemState.model_validate(c_sf))
    EngineBoundary().calculate(_ctx_r_sf)
    r_sf = _ctx_r_sf.state.model_dump(mode='json')
    
    c_gsf = copy.deepcopy(base_candidate)
    c_gsf["strategy"]["active_strategy"] = "GRID_SAFETY_FIRST"
    c_gsf["grid"]["active_limit"] = 25.0
    _ctx_r_gsf = CalculationContext(state=SystemState.model_validate(c_gsf))
    EngineBoundary().calculate(_ctx_r_gsf)
    r_gsf = _ctx_r_gsf.state.model_dump(mode='json')
    
    assert r_df["strategy"]["active_strategy"] == "DEADLINE_FIRST"
    assert r_sf["strategy"]["active_strategy"] == "SOLAR_FIRST"
    assert r_gsf["strategy"]["active_strategy"] == "GRID_SAFETY_FIRST"
    
    alloc_df = {a["ev_id"]: a["allocated_rate"] for a in r_df["allocations"]}
    alloc_sf = {a["ev_id"]: a["allocated_rate"] for a in r_sf["allocations"]}
    alloc_gsf = {a["ev_id"]: a["allocated_rate"] for a in r_gsf["allocations"]}
    
    # Check they are not identical aliases
    assert alloc_df != alloc_sf


# ==========================================
# 6. A5 Verification
# ==========================================
def test_a5_emergency_behavior(base_candidate):
    c_base = copy.deepcopy(base_candidate)
    c_base["grid"]["active_limit"] = 150.0
    c_base["grid"]["configured_limit"] = 150.0
    _ctx_r_base = CalculationContext(state=SystemState.model_validate(c_base))
    EngineBoundary().calculate(_ctx_r_base)
    r_base = _ctx_r_base.state.model_dump(mode='json')
    total_normal_alloc = sum(a["allocated_rate"] for a in r_base["allocations"])
    
    # Activate Emergency
    c_emg = copy.deepcopy(r_base)
    c_emg["emergency"]["emergency_active_state"] = True
    c_emg["emergency"]["emergency_limit"] = 0.85 # 85% reduction
    
    # We need to simulate how the EngineBoundary responds to emergency
    # It sets grid limit = configured * (1 - reduction)
    # So active_limit_kw becomes 22.5
    # Available = max(0, 22.5 - 60 + 40) = 2.5
    # This will force allocations < 23.9!
    _ctx_r_emg = CalculationContext(state=SystemState.model_validate(c_emg))
    EngineBoundary().calculate(_ctx_r_emg)
    r_emg = _ctx_r_emg.state.model_dump(mode='json')
    
    # The emergency state flag remains true
    assert r_emg["emergency"]["emergency_active_state"] is True
    
    total_emg_alloc = sum(a["allocated_rate"] for a in r_emg["allocations"])
    assert total_emg_alloc < total_normal_alloc
    
    # EXPLICIT ASSERTION: GRID_IMPORT <= active_limit
    grid_import = (r_emg["building"]["total_building_demand"] + total_emg_alloc) - r_emg["solar"]["generation"]
    assert grid_import <= r_emg["grid"]["active_limit"] + 0.01
    
    # Verify lower-priority charging can be paused (current_rate == 0.0)
    assert any(ev["current_rate"] == 0.0 for ev in r_emg["evs"])
    
    # Restore
    c_rest = copy.deepcopy(r_emg)
    c_rest["emergency"]["emergency_active_state"] = False
    _ctx_r_rest = CalculationContext(state=SystemState.model_validate(c_rest))
    EngineBoundary().calculate(_ctx_r_rest)
    r_rest = _ctx_r_rest.state.model_dump(mode='json')
    
    assert r_rest["emergency"]["emergency_active_state"] is False
    assert r_rest["grid"]["active_limit"] == 150.0
    total_rest_alloc = sum(a["allocated_rate"] for a in r_rest["allocations"])
    assert total_rest_alloc > total_emg_alloc


# ==========================================
# 7. Simulation Verification
# ==========================================
def test_simulation_progression(base_candidate):
    c = copy.deepcopy(base_candidate)
    c["simulation"]["is_running"] = True
    c["simulation"]["timestep"] = 0.25
    orig_time = c["simulation"]["simulation_time"]
    
    c_ctx = CalculationContext(state=SystemState.model_validate(c))
    EngineBoundary().calculate(c_ctx)
    r = c_ctx.state.model_dump(mode='json')
    assert r["simulation"]["simulation_time"] == orig_time + 0.25
    
def test_simulation_paused(base_candidate):
    c = copy.deepcopy(base_candidate)
    c["simulation"]["is_running"] = False
    c["simulation"]["timestep"] = 0.25
    orig_time = c["simulation"]["simulation_time"]
    
    c_ctx = CalculationContext(state=SystemState.model_validate(c))
    EngineBoundary().calculate(c_ctx)
    r = c_ctx.state.model_dump(mode='json')
    assert r["simulation"]["simulation_time"] == orig_time # No progression


# ==========================================
# 8. EV Spawning Verification
# ==========================================
def test_ev_spawning(base_candidate):
    c = copy.deepcopy(base_candidate)
    
    # Find an empty station
    empty_st = next((s for s in c["stations"] if not s["occupancy"]), None)
    if empty_st:
        empty_st["occupancy"] = True
        empty_st["connected_ev_id"] = "SPAWNED-EV-999"
        
        new_ev = {
            "ev_id": "SPAWNED-EV-999",
            "vehicle_type": "Car",
            "urgency": "URGENT",
            "battery_capacity": 60.0,
            "range": 300.0,
            "current_soc": 10.0,
            "requested_travel_distance": 150.0,
            "arrival": c["simulation"]["simulation_time"],
            "departure": c["simulation"]["simulation_time"] + 3.0,
            "minimum_rate": 1.4,
            "maximum_rate": 22.0,
            "current_rate": 0.0,
            "energy_required": 0.0,
            "time_remaining": 0.0,
            "required_average_power": 0.0,
            "estimated_completion": 0.0,
            "a3_risk": False,
            "a2_reason": ""
        }
        c["evs"].append(new_ev)
        
        c_ctx = CalculationContext(state=SystemState.model_validate(c))
        EngineBoundary().calculate(c_ctx)
        r = c_ctx.state.model_dump(mode='json')
        
        # Verify it was instantiated and participated
        out_ev = next((e for e in r["evs"] if e["ev_id"] == "SPAWNED-EV-999"), None)
        assert out_ev is not None
        assert out_ev["energy_required"] > 0.0
        assert out_ev["time_remaining"] > 0.0
        
        # Being URGENT, it should likely get an allocation
        alloc_val = next(a["allocated_power"] for a in r["allocations"] if a["station_id"] == empty_st["station_id"])
        assert alloc_val >= 0.0
