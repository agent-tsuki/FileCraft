"""
Main FastAPI application with comprehensive configuration and enhanced documentation.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_app_config
from app.core.app_logging import setup_logging
from app.core.api_config import get_openapi_schema, get_api_tags, api_config
from app.core.security import get_default_security_headers
from app.dependencies import get_uptime
from app.middleware import setup_exception_handlers
from app.middleware.request_logging import LoggingMiddleware
from app.router.converters import compression, images, audio, video
from app.router.encoder_decoder import encoder_decoder_router
from app.schemas.responses import SystemCheckResponse

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("FileCraft application starting up...")
    yield
    # Shutdown
    logger.info("FileCraft application shutting down...")


def create_application() -> FastAPI:
    """Create and configure comprehensive FastAPI application."""
    # Get configuration
    config = get_app_config()

    # Get OpenAPI configuration
    openapi_config = config.get_openapi_config()

    # Note: Custom swagger_ui_parameters are defined inline to avoid conflicts

    # Create FastAPI app with comprehensive configuration
    app = FastAPI(
        title=openapi_config["title"],
        description=openapi_config["description"],
        version=openapi_config["version"],
        debug=config.debug,
        docs_url=openapi_config["docs_url"] if config.enable_swagger_ui else None,
        redoc_url=openapi_config["redoc_url"] if config.enable_redoc else None,
        openapi_url=openapi_config["openapi_url"] if config.enable_openapi else None,
        contact=openapi_config["contact"],
        license_info=openapi_config["license_info"],
        terms_of_service=openapi_config["terms_of_service"],
        lifespan=lifespan,
        openapi_tags=get_api_tags(),
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True,
            "docExpansion": "list",
            "filter": True,
        },
        # Response configuration
        default_response_class=JSONResponse,
        # Additional FastAPI configuration
        servers=[
            {
                "url": f"http://localhost:{config.external_port}",
                "description": f"{config.environment.title()} server (External)",
            },
            {
                "url": f"http://{config.host}:{config.port}",
                "description": f"{config.environment.title()} server (Internal)",
            },
        ],
    )

    # Set custom OpenAPI schema generator
    app.openapi = lambda: get_openapi_schema(app)

    # Setup exception handlers
    setup_exception_handlers(app)

    # Add security middleware
    if not config.debug and config.is_production():
        # Add trusted host middleware in production
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=config.allowed_hosts)

    # Add logging middleware
    app.add_middleware(LoggingMiddleware)

    # Add CORS middleware with enhanced configuration
    cors_config = config.get_cors_config()
    app.add_middleware(CORSMiddleware, **cors_config)

    # Add security headers middleware
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        """Add security headers to all responses."""
        response = await call_next(request)

        # Add default security headers
        security_headers = get_default_security_headers()
        for header_name, header_value in security_headers.items():
            response.headers[header_name] = header_value

        # Add rate limiting headers (if enabled)
        rate_limit_config = config.get_rate_limit_config()
        if rate_limit_config["enabled"]:
            response.headers["X-RateLimit-Limit"] = str(rate_limit_config["requests"])
            response.headers["X-RateLimit-Window"] = str(rate_limit_config["window"])

        return response

    # Include routers
    app.include_router(images.image_router)
    app.include_router(audio.audio_router)
    app.include_router(video.video_router)
    app.include_router(compression.compression_router)

    # Include new encoder/decoder system
    app.include_router(encoder_decoder_router)

    # API Information endpoint
    @app.get(
        "/api/info",
        tags=["System"],
        summary="API Information",
        description="Get comprehensive API information, features, and configuration",
        response_model=Dict[str, Any],
    )
    def api_info() -> Dict[str, Any]:
        """Get API information and capabilities."""
        return api_config.get_app_metadata()

    # Health check endpoint
    @app.get(
        "/health",
        response_model=SystemCheckResponse,
        tags=["System"],
        summary="Health check",
        description="Check if the service is running and get uptime information",
    )
    def health_check(uptime: float = Depends(get_uptime)) -> SystemCheckResponse:
        """Health check endpoint with uptime information."""
        return SystemCheckResponse(message="FileCraft is running", uptime=uptime)

    # Enhanced health check with detailed information
    @app.get(
        "/health/detailed",
        tags=["System"],
        summary="Detailed health check",
        description="Get detailed health information including system status and configuration",
    )
    def detailed_health_check(uptime: float = Depends(get_uptime)) -> Dict[str, Any]:
        """Detailed health check with system information."""
        return {
            "status": "healthy",
            "message": "FileCraft is running",
            "uptime_seconds": uptime,
            "version": config.version,
            "environment": config.environment,
            "features": {
                "async_processing": config.enable_async_processing,
                "batch_processing": config.enable_batch_processing,
                "real_time_processing": config.enable_real_time_processing,
                "rate_limiting": config.rate_limit_enabled,
                "metrics": config.enable_metrics,
                "authentication": False,  # Not implemented
            },
            "limits": {
                "max_upload_size_mb": config.max_upload_size // (1024 * 1024),
                "max_concurrent_tasks": config.max_concurrent_tasks,
                "task_timeout_seconds": config.task_timeout,
            },
            "timestamp": "2025-10-02T12:00:00Z",
        }

    # Configuration endpoint (non-sensitive information only)
    @app.get(
        "/api/config",
        tags=["System"],
        summary="API Configuration",
        description="Get public API configuration and settings",
    )
    def get_public_config() -> Dict[str, Any]:
        """Get public API configuration."""
        return {
            "api_version": config.version,
            "environment": config.environment,
            "debug_mode": config.debug,
            "documentation": {
                "swagger_ui": config.docs_url,
                "redoc": config.redoc_url,
                "openapi": config.openapi_url,
            },
            "rate_limiting": {
                "enabled": config.rate_limit_enabled,
                "requests_per_window": (
                    config.rate_limit_requests if config.rate_limit_enabled else None
                ),
                "window_seconds": (
                    config.rate_limit_window if config.rate_limit_enabled else None
                ),
            },
            "file_processing": {
                "max_upload_size_mb": config.max_upload_size // (1024 * 1024),
                "supported_extensions": config.allowed_file_extensions,
                "async_processing": config.enable_async_processing,
                "batch_processing": config.enable_batch_processing,
            },
            "authentication": {
                "enabled": False,
                "methods": ["none"],  # Authentication not implemented
                "note": "Authentication is not implemented in this version",
            },
        }

    # Backward compatibility endpoint
    @app.get("/system-check", include_in_schema=False)
    def system_check():
        """Legacy system check endpoint for backward compatibility."""
        return {
            "status": True,
            "message": "File Craft is up",
        }

    return app


# Create the application instance
app = create_application()
