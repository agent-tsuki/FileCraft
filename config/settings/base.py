from pydantic_settings import BaseSettings, SettingsConfigDict

from .config import BASE_DIR


class Settings(BaseSettings):
    # Project configuration
    PROJECT_NAME: str
    DEBUG: bool
    DOCS: str

    # Database configuration
    DB_PORT: int
    DB_HOSTNAME: str
    DB_DATABASE: str
    DB_USER: str
    DB_PASSWORD: str
    
    # Redis configuration for Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Image processing configuration
    ENABLE_ASYNC_PROCESSING: bool = True
    MAX_IMAGE_SIZE_MB: int = 50
    IMAGE_QUALITY_DEFAULT: int = 85
    
    # Celery configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8"
    )
