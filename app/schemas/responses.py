"""
Response schemas for the FileCraft API.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel


class BaseResponse(BaseModel):
    """Base response model."""

    status: bool
    message: str


class ErrorResponse(BaseResponse):
    """Error response model."""

    status: bool = False
    error_type: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class SuccessResponse(BaseResponse):
    """Success response model."""

    status: bool = True


class FileProcessingResponse(SuccessResponse):
    """Response for successful file processing."""

    filename: str
    original_size: Optional[int] = None
    processed_size: Optional[int] = None
    compression_ratio: Optional[float] = None


class SystemCheckResponse(SuccessResponse):
    """Response for system check endpoint."""

    version: str = "1.0.0"
    uptime: Optional[float] = None
