"""
Custom exceptions for the FileCraft application.
"""

from typing import Any, Dict, Optional


class FileCraftException(Exception):
    """Base exception class for FileCraft."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class FileValidationError(FileCraftException):
    """Exception raised when file validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class FileSizeError(FileValidationError):
    """Exception raised when file size exceeds limits."""

    def __init__(self, file_type: str, max_size: int, actual_size: int):
        message = f"File size {actual_size} bytes exceeds maximum allowed {max_size} bytes for {file_type}"
        details = {
            "file_type": file_type,
            "max_size": max_size,
            "actual_size": actual_size,
        }
        super().__init__(message, details)


class FileProcessingError(FileCraftException):
    """Exception raised during file processing."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class ImageProcessingError(FileProcessingError):
    """Exception raised during image processing."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Image processing failed: {message}", details)


class CompressionError(FileProcessingError):
    """Exception raised during compression operations."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Compression failed: {message}", details)
