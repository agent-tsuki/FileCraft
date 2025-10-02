"""
Global exception handler middleware.
"""

import logging
import traceback
from typing import Union

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.exceptions import FileCraftException

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """Set up global exception handlers for the application."""

    @app.exception_handler(FileCraftException)
    async def filecraft_exception_handler(
        request: Request, exc: FileCraftException
    ) -> JSONResponse:
        """Handle custom FileCraft exceptions."""
        logger.error(
            f"FileCraft exception: {exc.message}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "details": exc.details,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": False,
                "message": exc.message,
                "details": exc.details,
                "error_type": exc.__class__.__name__,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions."""
        logger.warning(
            f"HTTP exception: {exc.detail}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": False,
                "message": exc.detail,
                "error_type": "HTTPException",
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle request validation errors."""
        logger.error(
            f"Validation error: {exc.errors()}",
            extra={"path": request.url.path, "method": request.method},
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": False,
                "message": "Validation error",
                "details": exc.errors(),
                "error_type": "ValidationError",
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle all other exceptions."""
        logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc(),
            },
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": False,
                "message": "Internal server error",
                "error_type": "InternalServerError",
            },
        )
