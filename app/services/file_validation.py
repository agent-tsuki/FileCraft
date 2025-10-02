"""
File validation service with dependency injection.
"""
from os import path
from typing import Tuple

from fastapi import Depends

from app.core.config import AppConfig, get_config
from app.exceptions import FileValidationError, FileSizeError
from app.services.base import BaseService
from app.helpers.constants import EXTENSION_TYPE_MAP


class FileValidationService(BaseService):
    """Service for file validation operations."""
    
    def __init__(self, config: AppConfig):
        super().__init__(config)
        # Use the centralized extension mapping from constants
        self.extension_type_map = EXTENSION_TYPE_MAP
    
    def validate_file_size(self, file_size: int, file_type: str) -> bool:
        """
        Validate file size against configured limits.
        
        Args:
            file_size: Size of the file in bytes
            file_type: Type of the file (img, docs, pdf, advance)
            
        Returns:
            True if file size is within limits
            
        Raises:
            FileSizeError: If file size exceeds limits
        """
        max_size = self.config.max_upload_sizes.get(file_type)
        if not max_size:
            raise FileValidationError(f"Unsupported file type: {file_type}")
        
        if file_size > max_size:
            raise FileSizeError(file_type, max_size, file_size)
        
        self.log_operation("file_size_validated", {
            "file_type": file_type,
            "file_size": file_size,
            "max_size": max_size
        })
        
        return True
    
    def get_file_type(self, filename: str) -> Tuple[str, str]:
        """
        Determine file type from filename.
        
        Args:
            filename: Name of the file
            
        Returns:
            Tuple of (base_name, file_type)
        """
        if not filename:
            raise FileValidationError("Filename cannot be empty")
        
        base, ext = path.splitext(filename)
        ext = ext.lower().lstrip(".")
        file_type = self.extension_type_map.get(ext, ext or "unknown")
        
        self.log_operation("file_type_determined", {
            "filename": filename,
            "extension": ext,
            "file_type": file_type
        })
        
        return base, file_type
    
    def validate_filename(self, filename: str) -> str:
        """
        Validate and sanitize filename.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
            
        Raises:
            FileValidationError: If filename is invalid
        """
        if not filename or not filename.strip():
            raise FileValidationError("File is empty or without filename")
        
        # Remove any path components for security
        sanitized = path.basename(filename)
        
        self.log_operation("filename_validated", {
            "original": filename,
            "sanitized": sanitized
        })
        
        return sanitized


def get_file_validation_service(
    config: AppConfig = Depends(get_config)
) -> FileValidationService:
    """Dependency to inject file validation service."""
    return FileValidationService(config)