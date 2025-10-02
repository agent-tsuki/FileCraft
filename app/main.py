"""
Main FastAPI application with dependency injection and middleware.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_app_config
from app.core.logging import setup_logging
from app.dependencies import get_uptime
from app.middleware import setup_exception_handlers
from app.middleware.logging import LoggingMiddleware
from app.router.converters import base64, compression, images, audio
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
    """Create and configure FastAPI application."""
    # Get configuration
    config = get_app_config()
    
    # Create FastAPI app
    app = FastAPI(
        title="FileCraft",
        description="Professional file conversion and processing API",
        version="1.0.0",
        debug=config.debug,
        docs_url=config.docs_url,
        openapi_url="/api/openapi.json",
        lifespan=lifespan
    )
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    # Add middleware
    app.add_middleware(LoggingMiddleware)
    
    cors_config = config.get_cors_config()
    app.add_middleware(CORSMiddleware, **cors_config)
    
    # Include routers
    app.include_router(base64.base64_router)
    app.include_router(images.image_router)
    app.include_router(audio.audio_router)
    app.include_router(compression.compression_router)
    
    # Health check endpoint
    @app.get(
        "/health",
        response_model=SystemCheckResponse,
        tags=["System"],
        summary="Health check",
        description="Check if the service is running and get uptime information"
    )
    def health_check(uptime: float = Depends(get_uptime)) -> SystemCheckResponse:
        """Health check endpoint with uptime information."""
        return SystemCheckResponse(
            message="FileCraft is running",
            uptime=uptime
        )
    
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
