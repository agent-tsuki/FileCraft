"""
File compression service with dependency injection.
"""
import io
import os
import zlib
from typing import BinaryIO, Generator

from fastapi import Depends, UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.config import AppConfig, get_config
from app.exceptions import CompressionError, ImageProcessingError
from app.services.base import BaseService
from app.services.file_validation import FileValidationService, get_file_validation_service


class CompressionService(BaseService):
    """Service for file and image compression operations."""
    
    def __init__(self, config: AppConfig, validation_service: FileValidationService):
        super().__init__(config)
        self.validation_service = validation_service
        self.image_extensions = {"jpg", "jpeg", "png", "webp", "tiff", "bmp", "gif"}
    
    async def smart_compress_file(
        self,
        file: UploadFile,
        compression_level: int = 6,
        quality: int = 70,
        force_webp: bool = False
    ) -> BinaryIO:
        """
        Smart compression for files and images.
        
        Args:
            file: Uploaded file
            compression_level: Compression level for zlib (1-9)
            quality: Image quality for lossy formats (10-95)
            force_webp: Convert all images to WebP format
            
        Returns:
            BytesIO buffer containing compressed content
            
        Raises:
            CompressionError: If compression fails
        """
        try:
            # Validate inputs
            filename = self.validation_service.validate_filename(file.filename or "")
            
            if not (1 <= compression_level <= 9):
                raise CompressionError("Compression level must be between 1 and 9")
            
            if not (10 <= quality <= 95):
                raise CompressionError("Quality must be between 10 and 95")
            
            # Get file info
            content = await file.read()
            base_name, file_type = self.validation_service.get_file_type(filename)
            self.validation_service.validate_file_size(len(content), file_type)
            
            # Get file extension
            _, ext = os.path.splitext(filename)
            ext = ext.lower().strip(".")
            
            # Check if it's an image
            if ext in self.image_extensions:
                return await self._compress_image(
                    content, filename, quality, force_webp
                )
            else:
                return self._compress_binary_file(
                    content, filename, compression_level
                )
                
        except Exception as e:
            self.logger.error(f"Smart compression failed: {str(e)}")
            if isinstance(e, (CompressionError, ImageProcessingError)):
                raise
            raise CompressionError(f"Failed to compress file: {str(e)}")
    
    async def _compress_image(
        self,
        content: bytes,
        filename: str,
        quality: int,
        force_webp: bool
    ) -> BinaryIO:
        """Compress image with metadata removal and format optimization."""
        try:
            input_buffer = io.BytesIO(content)
            
            with Image.open(input_buffer) as image:
                # Remove all metadata
                data = list(image.getdata())
                image_no_meta = Image.new(image.mode, image.size)
                image_no_meta.putdata(data)
                
                # Convert to RGB if needed for JPEG compatibility
                if image_no_meta.mode in ("RGBA", "P"):
                    rgb_image = Image.new("RGB", image_no_meta.size, (255, 255, 255))
                    if image_no_meta.mode == "P":
                        image_no_meta = image_no_meta.convert("RGBA")
                    rgb_image.paste(image_no_meta, mask=image_no_meta.split()[-1] if image_no_meta.mode == "RGBA" else None)
                    image_no_meta = rgb_image
                
                output = io.BytesIO()
                
                # Choose output format
                target_format = "WEBP" if force_webp else image.format or "JPEG"
                
                save_kwargs = {
                    "optimize": True,
                    "quality": quality
                }
                
                if target_format == "PNG":
                    save_kwargs = {"optimize": True, "compress_level": 9}
                    del save_kwargs["quality"]
                
                image_no_meta.save(output, format=target_format, **save_kwargs)
                output.seek(0)
                
                self.log_operation("image_compressed", {
                    "filename": filename,
                    "original_size": len(content),
                    "compressed_size": len(output.getvalue()),
                    "compression_ratio": len(output.getvalue()) / len(content),
                    "format": target_format,
                    "quality": quality
                })
                
                return output
                
        except UnidentifiedImageError:
            raise ImageProcessingError("Invalid or corrupted image format")
        except Exception as e:
            raise ImageProcessingError(f"Image compression failed: {str(e)}")
    
    def _compress_binary_file(
        self,
        content: bytes,
        filename: str,
        compression_level: int
    ) -> BinaryIO:
        """Compress binary file using zlib."""
        try:
            buffer = io.BytesIO(content)
            output = io.BytesIO()
            
            compressor = zlib.compressobj(compression_level)
            
            # Process in chunks
            chunk_size = self.config.chunk_size
            while True:
                chunk = buffer.read(chunk_size)
                if not chunk:
                    break
                compressed_chunk = compressor.compress(chunk)
                if compressed_chunk:
                    output.write(compressed_chunk)
            
            # Flush remaining data
            final_chunk = compressor.flush()
            if final_chunk:
                output.write(final_chunk)
            
            output.seek(0)
            
            self.log_operation("binary_file_compressed", {
                "filename": filename,
                "original_size": len(content),
                "compressed_size": len(output.getvalue()),
                "compression_ratio": len(output.getvalue()) / len(content),
                "compression_level": compression_level
            })
            
            return output
            
        except Exception as e:
            raise CompressionError(f"Binary file compression failed: {str(e)}")


def get_compression_service(
    config: AppConfig = Depends(get_config),
    validation_service: FileValidationService = Depends(get_file_validation_service)
) -> CompressionService:
    """Dependency to inject compression service."""
    return CompressionService(config, validation_service)