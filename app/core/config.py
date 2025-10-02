"""
Core configuration and dependencies for the FastAPI application.
"""
from functools import lru_cache
from typing import Any, Dict

from fastapi import Depends
from config.settings import settings


class AppConfig:
    """Application configuration class."""
    
    def __init__(self):
        self.debug = settings.DEBUG
        self.project_name = settings.PROJECT_NAME
        self.docs_url = settings.DOCS
        self.allowed_origins = ["*"]  # Configure this based on environment
        self.max_upload_sizes = {
            "img": 10485760,      # 10MB
            "docs": 5242880,      # 5MB
            "pdf": 15728640,      # 15MB
            "advance": 104857600  # 100MB
        }
        self.chunk_size = 8192
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration."""
        return {
            "allow_origins": self.allowed_origins,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }


@lru_cache()
def get_app_config() -> AppConfig:
    """Get cached application configuration."""
    return AppConfig()


def get_config(config: AppConfig = Depends(get_app_config)) -> AppConfig:
    """Dependency to inject configuration."""
    return config