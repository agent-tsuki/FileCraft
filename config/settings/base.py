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

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8"
    )
