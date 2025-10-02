"""
Request models for the FileCraft API.
"""

from typing import Optional
from pydantic import BaseModel, Field


class FileProcessingRequest(BaseModel):
    """Base model for file processing requests."""

    compress: bool = Field(default=False, description="Whether to compress the file")


class ImageConversionRequest(BaseModel):
    """Model for image conversion requests."""

    target_format: str = Field(..., description="Target image format")
    quality: int = Field(default=85, ge=1, le=100, description="Image quality (1-100)")


class CompressionRequest(BaseModel):
    """Model for file compression requests."""

    compression_level: int = Field(
        default=6, ge=1, le=9, description="Compression level (1-9)"
    )
    quality: int = Field(default=70, ge=10, le=95, description="Image quality (10-95)")
    force_webp: bool = Field(default=False, description="Convert images to WebP")
