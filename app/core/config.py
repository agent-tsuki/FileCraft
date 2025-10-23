"""
Core configuration and dependencies for the FastAPI application.
"""

from functools import lru_cache
from typing import Any, Dict, List, Optional

from fastapi import Depends
from config.settings import settings


class AppConfig:
    """Comprehensive application configuration class."""

    def __init__(self):
        # ===== API Configuration =====
        self.project_name = settings.PROJECT_NAME
        self.project_description = settings.PROJECT_DESCRIPTION
        self.version = settings.VERSION
        self.api_v1_prefix = settings.API_V1_PREFIX
        self.debug = settings.DEBUG

        # Documentation settings
        self.docs_url = settings.DOCS if settings.ENABLE_DOCS else None
        self.redoc_url = settings.REDOC_URL if settings.ENABLE_REDOC else None
        self.openapi_url = settings.OPENAPI_URL if settings.ENABLE_OPENAPI else None
        self.enable_swagger_ui = settings.ENABLE_SWAGGER_UI
        self.enable_redoc = settings.ENABLE_REDOC
        self.enable_openapi = settings.ENABLE_OPENAPI

        # ===== Server Configuration =====
        self.host = settings.HOST
        self.port = settings.PORT
        self.external_port = settings.EXTERNAL_PORT
        self.workers = settings.WORKERS
        self.reload = settings.RELOAD
        self.log_level = settings.LOG_LEVEL

        # ===== Security Configuration =====
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

        # JWT Configuration
        self.jwt_secret_key = settings.JWT_SECRET_KEY
        self.jwt_algorithm = settings.JWT_ALGORITHM
        self.jwt_access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.jwt_refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS

        # API Key configuration
        self.api_key_name = settings.API_KEY_NAME
        self.api_key_header = settings.API_KEY_HEADER
        self.enable_api_key_auth = settings.ENABLE_API_KEY_AUTH

        # ===== CORS Configuration =====
        self.allowed_hosts = settings.ALLOWED_HOSTS
        self.cors_origins = settings.CORS_ORIGINS
        self.cors_allow_credentials = settings.CORS_ALLOW_CREDENTIALS
        self.cors_allow_methods = settings.CORS_ALLOW_METHODS
        self.cors_allow_headers = settings.CORS_ALLOW_HEADERS

        # ===== Rate Limiting =====
        self.rate_limit_enabled = settings.RATE_LIMIT_ENABLED
        self.rate_limit_requests = settings.RATE_LIMIT_REQUESTS
        self.rate_limit_window = settings.RATE_LIMIT_WINDOW
        self.rate_limit_per_ip = settings.RATE_LIMIT_PER_IP

        # ===== File Upload Configuration =====
        self.max_upload_size = settings.MAX_UPLOAD_SIZE
        self.allowed_file_extensions = settings.ALLOWED_FILE_EXTENSIONS

        # Legacy upload size limits for backward compatibility
        self.max_upload_sizes = {
            "img": settings.MAX_IMAGE_SIZE_MB * 1024 * 1024,
            "audio": settings.MAX_AUDIO_SIZE_MB * 1024 * 1024,
            "video": settings.MAX_VIDEO_SIZE_MB * 1024 * 1024,
            "docs": 5 * 1024 * 1024,  # 5MB
            "pdf": 15 * 1024 * 1024,  # 15MB
            "advance": 100 * 1024 * 1024,  # 100MB
        }
        self.chunk_size = 8192

        # ===== DATABASE CONFIGURATION =====
        self.database_url = settings.DATABASE_URL
        self.db_host = settings.DB_HOSTNAME
        self.db_port = settings.DB_PORT
        self.db_name = settings.DB_DATABASE
        self.db_user = settings.DB_USER
        self.db_password = settings.DB_PASSWORD

        # ===== REDIS CONFIGURATION =====
        self.redis_url = settings.REDIS_URL
        self.redis_host = settings.REDIS_HOST
        self.redis_port = settings.REDIS_PORT
        self.redis_db = settings.REDIS_DB
        self.redis_password = settings.REDIS_PASSWORD
        self.redis_ssl = settings.REDIS_SSL

        # ===== CELERY CONFIGURATION =====
        self.celery_broker_url = settings.CELERY_BROKER_URL
        self.celery_result_backend = settings.CELERY_RESULT_BACKEND
        self.celery_task_serializer = settings.CELERY_TASK_SERIALIZER
        self.celery_result_serializer = settings.CELERY_RESULT_SERIALIZER
        self.celery_accept_content = settings.CELERY_ACCEPT_CONTENT
        self.celery_timezone = settings.CELERY_TIMEZONE
        self.celery_enable_utc = settings.CELERY_ENABLE_UTC
        self.celery_task_track_started = settings.CELERY_TASK_TRACK_STARTED
        self.celery_task_time_limit = settings.CELERY_TASK_TIME_LIMIT
        self.celery_task_soft_time_limit = settings.CELERY_TASK_SOFT_TIME_LIMIT

        # ===== Processing Configuration =====
        self.enable_async_processing = settings.ENABLE_ASYNC_PROCESSING
        self.max_concurrent_tasks = settings.MAX_CONCURRENT_TASKS
        self.task_timeout = settings.TASK_TIMEOUT

        # Image processing configuration
        self.max_image_pixels = settings.MAX_IMAGE_PIXELS
        self.image_memory_limit = settings.IMAGE_MEMORY_LIMIT
        self.image_quality_default = settings.IMAGE_QUALITY_DEFAULT

        # Audio processing configuration
        self.audio_bitrate_default = settings.AUDIO_BITRATE_DEFAULT
        self.audio_sample_rate_default = settings.AUDIO_SAMPLE_RATE_DEFAULT

        # Video processing configuration
        self.video_bitrate_default = settings.VIDEO_BITRATE_DEFAULT
        self.video_fps_default = settings.VIDEO_FPS_DEFAULT
        self.video_resolution_default = settings.VIDEO_RESOLUTION_DEFAULT

        # ===== Monitoring & Logging =====
        self.enable_metrics = settings.ENABLE_METRICS
        self.metrics_endpoint = settings.METRICS_ENDPOINT
        self.enable_health_check = settings.ENABLE_HEALTH_CHECK
        self.health_check_endpoint = settings.HEALTH_CHECK_ENDPOINT

        # Logging configuration
        self.log_format = settings.LOG_FORMAT
        self.log_file = settings.LOG_FILE
        self.log_max_size = settings.LOG_MAX_SIZE
        self.log_backup_count = settings.LOG_BACKUP_COUNT

        # ===== Feature Flags =====
        self.enable_admin_panel = settings.ENABLE_ADMIN_PANEL
        self.enable_webhooks = settings.ENABLE_WEBHOOKS
        self.enable_batch_processing = settings.ENABLE_BATCH_PROCESSING
        self.enable_real_time_processing = settings.ENABLE_REAL_TIME_PROCESSING

        # ===== Third-party Services - ALL DISABLED FOR LOCAL =====
        self.enable_s3_storage = False
        self.enable_email_notifications = False
        self.webhook_secret = settings.WEBHOOK_SECRET
        self.webhook_timeout = settings.WEBHOOK_TIMEOUT
        self.max_webhook_retries = settings.MAX_WEBHOOK_RETRIES

        # ===== Cache Configuration =====
        self.cache_ttl = settings.CACHE_TTL
        self.enable_response_cache = settings.ENABLE_RESPONSE_CACHE
        self.cache_max_size = settings.CACHE_MAX_SIZE

        # ===== Environment Configuration =====
        self.environment = settings.ENVIRONMENT
        self.sentry_dsn = settings.SENTRY_DSN
        self.enable_profiling = settings.ENABLE_PROFILING

        # ===== API Documentation Configuration =====
        self.contact_name = settings.CONTACT_NAME
        self.contact_email = settings.CONTACT_EMAIL
        self.contact_url = settings.CONTACT_URL
        self.license_name = settings.LICENSE_NAME
        self.license_url = settings.LICENSE_URL
        self.terms_of_service = settings.TERMS_OF_SERVICE

    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration."""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": self.cors_allow_credentials,
            "allow_methods": self.cors_allow_methods,
            "allow_headers": self.cors_allow_headers,
            "expose_headers": [
                "X-Total-Count",
                "X-Rate-Limit-Limit",
                "X-Rate-Limit-Remaining",
                "X-Rate-Limit-Reset",
            ],
            "max_age": 600,  # Cache preflight requests for 10 minutes
        }

    def get_openapi_config(self) -> Dict[str, Any]:
        """Get OpenAPI configuration for enhanced documentation."""
        return {
            "title": self.project_name,
            "description": self.project_description,
            "version": self.version,
            "openapi_url": self.openapi_url,
            "docs_url": self.docs_url,
            "redoc_url": self.redoc_url,
            "contact": {
                "name": self.contact_name,
                "email": self.contact_email,
                "url": self.contact_url,
            },
            "license_info": {
                "name": self.license_name,
                "url": self.license_url,
            },
            "terms_of_service": self.terms_of_service,
        }

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return {
            "secret_key": self.secret_key,
            "algorithm": self.algorithm,
            "access_token_expire_minutes": self.access_token_expire_minutes,
            "jwt_secret_key": self.jwt_secret_key,
            "jwt_algorithm": self.jwt_algorithm,
            "api_key_header": self.api_key_header,
            "enable_api_key_auth": self.enable_api_key_auth,
        }

    def get_rate_limit_config(self) -> Dict[str, Any]:
        """Get rate limiting configuration."""
        return {
            "enabled": self.rate_limit_enabled,
            "requests": self.rate_limit_requests,
            "window": self.rate_limit_window,
            "per_ip": self.rate_limit_per_ip,
        }

    def get_celery_config(self) -> Dict[str, Any]:
        """Get Celery configuration."""
        return {
            "broker_url": self.celery_broker_url,
            "result_backend": self.celery_result_backend,
            "task_serializer": self.celery_task_serializer,
            "result_serializer": self.celery_result_serializer,
            "accept_content": self.celery_accept_content,
            "timezone": self.celery_timezone,
            "enable_utc": self.celery_enable_utc,
            "task_track_started": self.celery_task_track_started,
            "task_time_limit": self.celery_task_time_limit,
            "task_soft_time_limit": self.celery_task_soft_time_limit,
        }

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


@lru_cache()
def get_app_config() -> AppConfig:
    """Get cached application configuration."""
    return AppConfig()


def get_config(config: AppConfig = Depends(get_app_config)) -> AppConfig:
    """Dependency to inject configuration."""
    return config
