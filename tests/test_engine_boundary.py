from app.core.engine_boundary import EngineBoundary, CalculationContext, CalculationResult
from app.models.pydantic_state import SystemState

def test_engine_boundary_returns_result():
    boundary = EngineBoundary()
    state = SystemState(grid={"configured_limit": 100.0, "active_limit": 100.0}, emergency={"emergency_limit": 50.0})
    context = CalculationContext(state=state)
    
    result = boundary.calculate(context)
    
    assert isinstance(result, CalculationResult)
