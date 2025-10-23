from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

from .config import BASE_DIR


class Settings(BaseSettings):
    # ===== API Configuration =====
    PROJECT_NAME: str = "FileCraft"
    PROJECT_DESCRIPTION: str = (
        "Professional file conversion and processing API with advanced encoding/decoding capabilities"
    )
    VERSION: str = "1.2.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Documentation settings
    DOCS: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/api/openapi.json"
    ENABLE_DOCS: bool = True

    # ===== Server Configuration =====
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    EXTERNAL_PORT: int = 8080  # Port exposed by Docker
    WORKERS: int = 4
    RELOAD: bool = False
    LOG_LEVEL: str = "info"

    # ===== Security Configuration =====
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # JWT Configuration
    JWT_SECRET_KEY: str = "jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # API Key configuration
    API_KEY_NAME: str = "X-API-Key"
    API_KEY_HEADER: str = "X-API-Key"
    ENABLE_API_KEY_AUTH: bool = False

    # ===== CORS Configuration =====
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://0.0.0.0:8080",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*",  # Allow all origins for development
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = [
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS",
        "PATCH",
        "HEAD",
    ]
    CORS_ALLOW_HEADERS: List[str] = [
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-API-Key",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Methods",
    ]

    # ===== Rate Limiting =====
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # seconds (1 hour)
    RATE_LIMIT_PER_IP: int = 1000  # requests per IP per window

    # ===== File Upload Configuration =====
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB for local
    ALLOWED_FILE_EXTENSIONS: List[str] = [
        # Images
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".webp",
        ".tiff",
        ".svg",
        # Audio
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
        ".m4a",
        ".wma",
        # Video
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
        # Documents
        ".pdf",
        ".txt",
        ".doc",
        ".docx",
        ".rtf",
        ".odt",
        # Archives
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".bz2",
    ]

    # ===== DATABASE CONFIGURATION (Docker/Render ready) =====
    DB_PORT: int = 5432
    DB_HOSTNAME: str = "db"  # Docker service name, fallback to localhost
    DB_DATABASE: str = "filecraft"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DATABASE_URL: Optional[str] = None

    # ===== REDIS CONFIGURATION (Docker/Render ready) =====
    REDIS_URL: str = "redis://redis:6379/0"  # Docker service name
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SSL: bool = False

    # ===== CELERY CONFIGURATION =====
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 30 * 60  # 30 minutes
    CELERY_TASK_SOFT_TIME_LIMIT: int = 25 * 60  # 25 minutes

    # ===== PROCESSING CONFIGURATION =====
    ENABLE_ASYNC_PROCESSING: bool = True  # Enabled for Docker/Render
    MAX_CONCURRENT_TASKS: int = 4
    TASK_TIMEOUT: int = 300  # 5 minutes

    # Image processing - reduced for local
    MAX_IMAGE_SIZE_MB: int = 20
    IMAGE_QUALITY_DEFAULT: int = 85
    MAX_IMAGE_PIXELS: int = 178956970  # 178MP limit for PIL
    IMAGE_MEMORY_LIMIT: int = 256 * 1024 * 1024  # 256MB

    # Audio processing - reduced for local
    MAX_AUDIO_SIZE_MB: int = 50
    AUDIO_BITRATE_DEFAULT: int = 128
    AUDIO_SAMPLE_RATE_DEFAULT: int = 44100

    # Video processing - reduced for local
    MAX_VIDEO_SIZE_MB: int = 100
    VIDEO_BITRATE_DEFAULT: str = "1M"
    VIDEO_FPS_DEFAULT: int = 30
    VIDEO_RESOLUTION_DEFAULT: str = "1280x720"

    # ===== Monitoring & Logging =====
    ENABLE_METRICS: bool = True
    METRICS_ENDPOINT: str = "/metrics"
    ENABLE_HEALTH_CHECK: bool = True
    HEALTH_CHECK_ENDPOINT: str = "/health"

    # Logging configuration
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = "app.log"
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5

    # ===== Feature Flags =====
    ENABLE_SWAGGER_UI: bool = True
    ENABLE_REDOC: bool = True
    ENABLE_OPENAPI: bool = True
    ENABLE_ADMIN_PANEL: bool = False
    ENABLE_WEBHOOKS: bool = False
    ENABLE_BATCH_PROCESSING: bool = True
    ENABLE_REAL_TIME_PROCESSING: bool = True

    # ===== DISABLED EXTERNAL SERVICES FOR LOCAL =====
    # AWS S3 - Disabled for local development
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None
    ENABLE_S3_STORAGE: bool = False

    # Email - Disabled for local development
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    EMAIL_FROM: Optional[str] = None
    ENABLE_EMAIL_NOTIFICATIONS: bool = False

    # Webhooks - Disabled for local development
    WEBHOOK_SECRET: Optional[str] = None
    WEBHOOK_TIMEOUT: int = 30
    MAX_WEBHOOK_RETRIES: int = 3

    # ===== Cache Configuration =====
    CACHE_TTL: int = 3600  # 1 hour
    ENABLE_RESPONSE_CACHE: bool = True
    CACHE_MAX_SIZE: int = 1000  # Max number of cached items

    # ===== Environment Configuration =====
    ENVIRONMENT: str = "development"  # development, staging, production
    SENTRY_DSN: Optional[str] = None  # For error tracking
    ENABLE_PROFILING: bool = False

    # ===== API Documentation Configuration =====
    CONTACT_NAME: str = "FileCraft Support"
    CONTACT_EMAIL: str = "support@filecraft.com"
    CONTACT_URL: str = "https://filecraft.com/support"
    LICENSE_NAME: str = "MIT License"
    LICENSE_URL: str = "https://opensource.org/licenses/MIT"
    TERMS_OF_SERVICE: str = "https://filecraft.com/terms"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8", case_sensitive=True
    )
