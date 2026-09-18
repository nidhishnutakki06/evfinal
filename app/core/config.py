import os
from pydantic_settings import BaseSettings

# Base directory is BACKEND-DATABASE (2 levels up from app/core)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings(BaseSettings):
    project_name: str = "SH-305 Backend"
    
    # Database Settings. Use absolute path for safety.
    sqlite_url: str = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'sh305.db')}"
    
settings = Settings()
