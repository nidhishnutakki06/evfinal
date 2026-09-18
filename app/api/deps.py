from app.services.state_manager import RuntimeStateManager
from app.core.engine_boundary import EngineBoundary
from app.services.validation import StateValidator
from app.services.control import ControlService

# Singleton State Manager for the entire application
state_manager = RuntimeStateManager()
engine_boundary = EngineBoundary()
state_validator = StateValidator()
control_service = ControlService(state_manager, engine_boundary, state_validator)

def get_state_manager() -> RuntimeStateManager:
    return state_manager

def get_control_service() -> ControlService:
    return control_service
