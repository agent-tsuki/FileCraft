"""
Enhanced image processing service with advanced features and optimization.
"""

import io
import asyncio
from typing import BinaryIO, Dict, Any, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor
import logging

from fastapi import Depends, UploadFile
from PIL import Image, ImageOps, ImageFilter

from app.core.config import AppConfig, get_config
from app.exceptions import ImageProcessingError
from app.services.base import BaseService
from app.services.file_validation import (
    FileValidationService,
    get_file_validation_service,
)
from app.helpers.constants import (
    IMAGE_FORMATS,
    SUPPORTED_OUTPUT_FORMATS,
    QUALITY_PRESETS,
    SIZE_PRESETS,
    IMAGE_OPTIMIZATION,
)

# Check if Celery is available without importing tasks
try:
    import celery

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

logger = logging.getLogger(__name__)


class ImageService(BaseService):
    """Enhanced service for image processing operations with advanced features."""

    def __init__(self, config: AppConfig, validation_service: FileValidationService):
        super().__init__(config)
        self.validation_service = validation_service
        self.supported_formats = set(SUPPORTED_OUTPUT_FORMATS)
        self.executor = ThreadPoolExecutor(
            max_workers=4
        )  # For CPU-intensive operations

    async def convert_image_format(
        self,
        image_file: UploadFile,
        target_format: str,
        quality: int = 85,
        use_async: bool = False,
        resize_options: Optional[Dict[str, Any]] = None,
        optimization_level: str = "medium",
    ) -> BinaryIO:
        """
        Convert image to specified format with enhanced options.

        Args:
            image_file: Uploaded image file
            target_format: Target format (jpeg, png, webp, etc.)
            quality: Image quality for lossy formats (1-100)
            use_async: Whether to use Celery for background processing
            resize_options: Optional resize parameters
            optimization_level: Optimization level (low, medium, high, maximum)

        Returns:
            BytesIO buffer containing converted image

        Raises:
            ImageProcessingError: If conversion fails
        """
        try:
            # Validate inputs
            filename = self.validation_service.validate_filename(
                image_file.filename or ""
            )
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

            # Use Celery for background processing if requested and available
            if use_async and CELERY_AVAILABLE and self._is_redis_available():
                try:
                    from app.tasks.image_tasks import convert_image_async

                    task = convert_image_async.delay(
                        content,
                        target_format,
                        quality,
                        optimization_level,
                        resize_options,
                    )
                    return {"task_id": task.id, "status": "processing"}
                except Exception:
                    # Fall back to synchronous processing
                    pass

            # Process synchronously
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._convert_image_sync,
                content,
                target_format,
                quality,
                resize_options,
                optimization_level,
            )

            self.log_operation(
                "image_converted",
                {
                    "filename": filename,
                    "target_format": target_format,
                    "original_size": len(content),
                    "converted_size": len(result.getvalue()) if result else 0,
                    "quality": quality,
                    "optimization_level": optimization_level,
                },
            )

            return result

        except Exception as e:
            self.logger.error(f"Image conversion failed: {str(e)}")
            if isinstance(e, ImageProcessingError):
                raise
            raise ImageProcessingError(f"Failed to convert image: {str(e)}")

    def _convert_image_sync(
        self,
        image_data: bytes,
        target_format: str,
        quality: int,
        resize_options: Optional[Dict[str, Any]],
        optimization_level: str,
    ) -> BinaryIO:
        """Synchronous image conversion for executor."""
        input_buffer = io.BytesIO(image_data)

        with Image.open(input_buffer) as img:
            # Auto-rotate based on EXIF
            img = ImageOps.exif_transpose(img)

            # Apply resize if specified
            if resize_options:
                img = self._resize_image(img, resize_options)

            # Apply optimization
            if optimization_level in ["high", "maximum"]:
                img = self._apply_optimization(img, optimization_level)

            # Handle transparency for JPEG
            if target_format in ("jpeg", "jpg") and img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                if img.mode == "RGBA":
                    background.paste(img, mask=img.split()[-1])
                img = background

            # Create output buffer
            output_buffer = io.BytesIO()

            # Determine save format and parameters
            save_format = (
                "JPEG" if target_format in ("jpeg", "jpg") else target_format.upper()
            )
            save_kwargs = self._get_save_parameters(
                save_format, quality, optimization_level
            )

            img.save(output_buffer, **save_kwargs)
            output_buffer.seek(0)

            return output_buffer

    def _resize_image(
        self, img: Image.Image, resize_options: Dict[str, Any]
    ) -> Image.Image:
        """Resize image based on options."""
        width = resize_options.get("width")
        height = resize_options.get("height")
        preset = resize_options.get("preset")
        maintain_aspect = resize_options.get("maintain_aspect", True)
        upscale = resize_options.get("upscale", False)

        if preset and preset in SIZE_PRESETS:
            width, height = SIZE_PRESETS[preset]

        if not width and not height:
            return img

        original_width, original_height = img.size

        if maintain_aspect:
            if width and height:
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
            elif width:
                ratio = width / original_width
                if ratio > 1 and not upscale:
                    return img
                height = int(original_height * ratio)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            elif height:
                ratio = height / original_height
                if ratio > 1 and not upscale:
                    return img
                width = int(original_width * ratio)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
        else:
            if not upscale and (width > original_width or height > original_height):
                return img
            img = img.resize((width, height), Image.Resampling.LANCZOS)

        return img

    def _apply_optimization(self, img: Image.Image, level: str) -> Image.Image:
        """Apply optimization based on level."""
        if level == "maximum":
            # Apply sharpening
            img = img.filter(
                ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3)
            )
        elif level == "high":
            img = img.filter(ImageFilter.SHARPEN)

        return img

    def _get_save_parameters(
        self, format_name: str, quality: int, optimization_level: str
    ) -> Dict[str, Any]:
        """Get optimal save parameters for format."""
        save_kwargs = {"format": format_name, "optimize": True}

        if format_name == "JPEG":
            save_kwargs.update(
                {
                    "quality": quality,
                    "progressive": optimization_level in ["high", "maximum"],
                    "subsampling": 0 if quality > 90 else 2,
                }
            )
        elif format_name == "PNG":
            compress_level = 9 if optimization_level in ["high", "maximum"] else 6
            save_kwargs["compress_level"] = compress_level
        elif format_name == "WEBP":
            save_kwargs.update(
                {
                    "quality": quality,
                    "method": 6 if optimization_level in ["high", "maximum"] else 4,
                    "lossless": quality == 100,
                }
            )
        elif format_name == "AVIF":
            save_kwargs.update(
                {
                    "quality": quality,
                    "speed": 1 if optimization_level in ["high", "maximum"] else 6,
                }
            )

        return save_kwargs

    async def batch_convert_images(
        self,
        images: List[UploadFile],
        target_format: str,
        quality: int = 85,
        optimization_level: str = "medium",
    ) -> Dict[str, Any]:
        """Convert multiple images in batch."""
        if not CELERY_AVAILABLE or not self._is_redis_available():
            raise ImageProcessingError("Batch processing requires Celery and Redis")

        # Prepare image data
        images_data = []
        for img_file in images:
            content = await img_file.read()
            images_data.append({"data": content, "filename": img_file.filename})

        # Submit batch task
        from app.tasks.image_tasks import batch_convert_images

        task = batch_convert_images.delay(
            images_data,
            {
                "target_format": target_format,
                "quality": quality,
                "optimization_level": optimization_level,
            },
        )

        return {"task_id": task.id, "status": "processing", "total_images": len(images)}

    async def optimize_image(
        self,
        image_file: UploadFile,
        optimization_type: str = "balanced",
        target_size_kb: Optional[int] = None,
    ) -> BinaryIO:
        """Optimize image for size or quality."""
        content = await image_file.read()

        if CELERY_AVAILABLE and self._is_redis_available():
            try:
                from app.tasks.image_tasks import optimize_image_async

                task = optimize_image_async.delay(
                    content, optimization_type, target_size_kb, True
                )
                return {"task_id": task.id, "status": "processing"}
            except Exception:
                # Fall back to synchronous processing
                pass

        # Fallback to synchronous processing
        return await asyncio.get_event_loop().run_in_executor(
            self.executor,
            self._optimize_image_sync,
            content,
            optimization_type,
            target_size_kb,
        )

    def _optimize_image_sync(
        self, image_data: bytes, optimization_type: str, target_size_kb: Optional[int]
    ) -> BinaryIO:
        """Synchronous image optimization."""
        input_buffer = io.BytesIO(image_data)

        with Image.open(input_buffer) as img:
            if optimization_type == "size":
                if target_size_kb:
                    return self._optimize_for_size(img, target_size_kb * 1024)
                else:
                    return self._convert_optimized(img, "webp", 80)
            elif optimization_type == "quality":
                return self._convert_optimized(img, "png", 100)
            else:  # balanced
                return self._convert_optimized(img, "webp", 90)

    def _optimize_for_size(self, img: Image.Image, target_bytes: int) -> BinaryIO:
        """Optimize image to target file size."""
        quality = 95

        while quality > 10:
            output_buffer = io.BytesIO()
            img.save(output_buffer, format="JPEG", quality=quality, optimize=True)
            if len(output_buffer.getvalue()) <= target_bytes:
                output_buffer.seek(0)
                return output_buffer
            quality -= 5

        # If still too large, resize
        scale = 0.9
        while scale > 0.3:
            resized = img.copy()
            new_size = (int(img.width * scale), int(img.height * scale))
            resized = resized.resize(new_size, Image.Resampling.LANCZOS)

            output_buffer = io.BytesIO()
            resized.save(output_buffer, format="JPEG", quality=80, optimize=True)
            if len(output_buffer.getvalue()) <= target_bytes:
                output_buffer.seek(0)
                return output_buffer
            scale -= 0.1

        # Final attempt
        output_buffer = io.BytesIO()
        img.save(output_buffer, format="JPEG", quality=30, optimize=True)
        output_buffer.seek(0)
        return output_buffer

    def _convert_optimized(
        self, img: Image.Image, format_name: str, quality: int
    ) -> BinaryIO:
        """Convert image with optimization."""
        output_buffer = io.BytesIO()
        save_kwargs = self._get_save_parameters(format_name.upper(), quality, "high")
        img.save(output_buffer, **save_kwargs)
        output_buffer.seek(0)
        return output_buffer

    async def get_image_info(self, image_file: UploadFile) -> Dict[str, Any]:
        """Get comprehensive image information."""
        content = await image_file.read()

        # Check if Celery is available and working
        if CELERY_AVAILABLE and self._is_redis_available():
            try:
                from app.tasks.optimization_tasks import analyze_image_stats

                task = analyze_image_stats.delay(content)
                return {"task_id": task.id, "status": "processing"}
            except Exception:
                # Fall back to synchronous processing
                pass

        # Synchronous analysis
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, self._analyze_image_sync, content
        )

    def _analyze_image_sync(self, image_data: bytes) -> Dict[str, Any]:
        """Synchronous image analysis."""
        with Image.open(io.BytesIO(image_data)) as img:
            return {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height,
                "file_size": len(image_data),
                "aspect_ratio": round(img.width / img.height, 2),
                "megapixels": round((img.width * img.height) / 1000000, 2),
                "color_depth": len(img.getbands()),
                "has_transparency": img.mode in ("RGBA", "LA")
                or "transparency" in img.info,
                "estimated_format": self._detect_format_by_content(img),
            }

    def _detect_format_by_content(self, img: Image.Image) -> str:
        """Detect the most suitable format for the image content."""
        if img.mode in ("RGBA", "LA") or "transparency" in img.info:
            return "PNG"  # Has transparency
        elif img.mode == "P":
            return "PNG"  # Palette mode
        elif img.mode in ("1", "L"):
            return "PNG"  # Grayscale or binary
        else:
            return "JPEG"  # Full color

    def _is_redis_available(self) -> bool:
        """Check if Redis is available for Celery tasks."""
        try:
            import redis

            r = redis.Redis.from_url(self.config.redis_url)
            r.ping()
            return True
        except Exception:
            return False


def get_image_service(
    config: AppConfig = Depends(get_config),
    validation_service: FileValidationService = Depends(get_file_validation_service),
) -> ImageService:
    """Dependency to inject image service."""
    return ImageService(config, validation_service)
