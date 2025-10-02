"""
Image processing service with dependency injection.
"""
import io
from typing import BinaryIO

from fastapi import Depends, UploadFile
from PIL import Image

from app.core.config import AppConfig, get_config
from app.exceptions import ImageProcessingError
from app.services.base import BaseService
from app.services.file_validation import FileValidationService, get_file_validation_service


class ImageService(BaseService):
    """Service for image processing operations."""
    
    def __init__(self, config: AppConfig, validation_service: FileValidationService):
        super().__init__(config)
        self.validation_service = validation_service
        self.supported_formats = {
            "jpeg", "jpg", "png", "webp", "bmp", "gif", "tiff", "ico"
        }
    
    async def convert_image_format(
        self,
        image_file: UploadFile,
        target_format: str,
        quality: int = 85
    ) -> BinaryIO:
        """
        Convert image to specified format.
        
        Args:
            image_file: Uploaded image file
            target_format: Target format (jpeg, png, webp, etc.)
            quality: Image quality for lossy formats (1-100)
            
        Returns:
            BytesIO buffer containing converted image
            
        Raises:
            ImageProcessingError: If conversion fails
        """
        try:
            # Validate inputs
            filename = self.validation_service.validate_filename(image_file.filename or "")
            target_format = target_format.lower()
            
            if target_format not in self.supported_formats:
                raise ImageProcessingError(f"Unsupported format: {target_format}")
            
            if not (1 <= quality <= 100):
                raise ImageProcessingError("Quality must be between 1 and 100")
            
            # Read and validate image
            content = await image_file.read()
            _, file_type = self.validation_service.get_file_type(filename)
            
            if file_type != "img":
                raise ImageProcessingError(f"File is not an image: {file_type}")
            
            self.validation_service.validate_file_size(len(content), file_type)
            
            # Process image
            input_buffer = io.BytesIO(content)
            
            with Image.open(input_buffer) as img:
                # Handle transparency for JPEG
                if target_format in ("jpeg", "jpg") and img.mode in ("RGBA", "LA", "P"):
                    # Convert to RGB for JPEG
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                    img = background
                
                # Create output buffer
                output_buffer = io.BytesIO()
                
                # Determine save format
                save_format = "JPEG" if target_format in ("jpeg", "jpg") else target_format.upper()
                
                # Save with appropriate parameters
                save_kwargs = {"format": save_format, "optimize": True}
                
                if save_format in ("JPEG", "WEBP"):
                    save_kwargs["quality"] = quality
                elif save_format == "PNG":
                    save_kwargs["compress_level"] = 9
                
                img.save(output_buffer, **save_kwargs)
                output_buffer.seek(0)
                
                self.log_operation("image_converted", {
                    "filename": filename,
                    "source_format": img.format,
                    "target_format": target_format,
                    "original_size": len(content),
                    "converted_size": len(output_buffer.getvalue()),
                    "quality": quality
                })
                
                return output_buffer
                
        except Exception as e:
            self.logger.error(f"Image conversion failed: {str(e)}")
            if isinstance(e, ImageProcessingError):
                raise
            raise ImageProcessingError(f"Failed to convert image: {str(e)}")


def get_image_service(
    config: AppConfig = Depends(get_config),
    validation_service: FileValidationService = Depends(get_file_validation_service)
) -> ImageService:
    """Dependency to inject image service."""
    return ImageService(config, validation_service)