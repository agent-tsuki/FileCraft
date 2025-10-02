"""
Global dependencies for the FastAPI application.
"""
import time
from functools import lru_cache

from fastapi import Depends

from app.core.config import AppConfig, get_config


class AppState:
    """Application state manager."""
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds."""
        return time.time() - self.start_time


@lru_cache()
def get_app_state() -> AppState:
    """Get cached application state."""
    return AppState()


def get_uptime(app_state: AppState = Depends(get_app_state)) -> float:
    """Dependency to get application uptime."""
    return app_state.get_uptime()