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
            "img": 50485760,      # 50MB (increased for high-res images)
            "audio": 209715200,   # 200MB for audio files
            "docs": 5242880,      # 5MB
            "pdf": 15728640,      # 15MB
            "video": 524288000,   # 500MB for video files
            "advance": 104857600  # 100MB
        }
        self.chunk_size = 8192
        
        # Redis configuration for Celery
        self.redis_url = getattr(settings, 'REDIS_URL', "redis://localhost:6379/0")
        
        # Image processing configuration
        self.max_image_pixels = 178956970  # 178MP limit for PIL
        self.image_memory_limit = 256 * 1024 * 1024  # 256MB
        self.enable_async_processing = getattr(settings, 'ENABLE_ASYNC_PROCESSING', True)
    
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