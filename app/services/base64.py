"""
Base64 conversion service with dependency injection.
"""
import io
import zlib
from base64 import b64encode
from typing import AsyncGenerator

from fastapi import Depends, UploadFile

from app.core.config import AppConfig, get_config
from app.exceptions import FileProcessingError
from app.services.base import BaseService
from app.services.file_validation import FileValidationService, get_file_validation_service


class Base64Service(BaseService):
    """Service for Base64 conversion operations."""
    
    def __init__(self, config: AppConfig, validation_service: FileValidationService):
        super().__init__(config)
        self.validation_service = validation_service
    
    async def convert_to_base64_stream(
        self,
        file: UploadFile,
        compress: bool = False
    ) -> AsyncGenerator[bytes, None]:
        """
        Convert file to base64 with streaming support.
        
        Args:
            file: Uploaded file
            compress: Whether to compress the file before encoding
            
        Yields:
            Base64 encoded chunks
            
        Raises:
            FileProcessingError: If conversion fails
        """
        try:
            # Validate filename
            filename = self.validation_service.validate_filename(file.filename or "")
            
            # Read file content
            content = await file.read()
            
            # Validate file size and type
            _, file_type = self.validation_service.get_file_type(filename)
            self.validation_service.validate_file_size(len(content), file_type)
            
            # Compress if requested
            if compress:
                content = zlib.compress(content)
                self.log_operation("file_compressed", {
                    "original_size": len(await file.read()) if hasattr(file, 'read') else 0,
                    "compressed_size": len(content)
                })
            
            # Stream base64 encoding
            buffer = io.BytesIO(content)
            chunk_size = self.config.chunk_size
            
            self.log_operation("base64_conversion_started", {
                "filename": filename,
                "file_size": len(content),
                "compressed": compress
            })
            
            while True:
                chunk = buffer.read(chunk_size)
                if not chunk:
                    break
                yield b64encode(chunk)
            
            self.log_operation("base64_conversion_completed", {
                "filename": filename
            })
            
        except Exception as e:
            self.logger.error(f"Base64 conversion failed: {str(e)}")
            if isinstance(e, (FileProcessingError, ValueError)):
                raise
            raise FileProcessingError(f"Failed to convert file to base64: {str(e)}")


def get_base64_service(
    config: AppConfig = Depends(get_config),
    validation_service: FileValidationService = Depends(get_file_validation_service)
) -> Base64Service:
    """Dependency to inject base64 service."""
    return Base64Service(config, validation_service)