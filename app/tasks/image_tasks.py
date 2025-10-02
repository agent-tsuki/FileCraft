"""
Celery tasks for image processing operations.
"""
import io
import os
import tempfile
from typing import Dict, Any, Optional, Tuple, List
import asyncio
from celery import current_task
from celery.exceptions import Retry

from app.celery_app import celery_app
from app.helpers.constants import (
    IMAGE_FORMATS, QUALITY_PRESETS, SIZE_PRESETS, 
    IMAGE_OPTIMIZATION, TASK_PRIORITIES
)

# Import image processing libraries
from PIL import Image, ImageOps, ImageFilter, ExifTags

# Optional advanced libraries
ADVANCED_LIBS = {}
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    ADVANCED_LIBS['heif'] = True
except ImportError:
    ADVANCED_LIBS['heif'] = False

try:
    import numpy as np
    ADVANCED_LIBS['numpy'] = True
except ImportError:
    ADVANCED_LIBS['numpy'] = False

try:
    import cv2
    ADVANCED_LIBS['opencv'] = True
except ImportError:
    ADVANCED_LIBS['opencv'] = False

try:
    from wand.image import Image as WandImage
    ADVANCED_LIBS['wand'] = True
except ImportError:
    ADVANCED_LIBS['wand'] = False

try:
    import rawpy
    ADVANCED_LIBS['rawpy'] = True
except ImportError:
    ADVANCED_LIBS['rawpy'] = False

try:
    from skimage import restoration
    ADVANCED_LIBS['skimage'] = True
except ImportError:
    ADVANCED_LIBS['skimage'] = False


@celery_app.task(
    bind=True,
    name="app.tasks.image_tasks.convert_image_async",
    max_retries=3,
    default_retry_delay=60
)
def convert_image_async(
    self,
    image_data: bytes,
    target_format: str,
    quality: int = 85,
    optimization_level: str = "medium",
    resize_options: Optional[Dict[str, Any]] = None,
    metadata_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convert image format asynchronously with advanced options.
    
    Args:
        image_data: Raw image data as bytes
        target_format: Target format (jpeg, png, webp, etc.)
        quality: Image quality (1-100)
        optimization_level: Optimization level (low, medium, high, maximum)
        resize_options: Dictionary with resize parameters
        metadata_options: Dictionary with metadata handling options
    
    Returns:
        Dictionary with converted image data and metadata
    """
    try:
        # Update task state
        self.update_state(state="PROCESSING", meta={"step": "initializing"})
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False) as temp_input:
            temp_input.write(image_data)
            temp_input_path = temp_input.name
        
        try:
            # Load image with appropriate library
            image, original_format = _load_image_optimized(temp_input_path)
            
            self.update_state(state="PROCESSING", meta={"step": "format_detection", "original_format": original_format})
            
            # Apply optimizations based on level
            if optimization_level in ["high", "maximum"]:
                image = _apply_advanced_optimization(image, optimization_level)
            
            self.update_state(state="PROCESSING", meta={"step": "optimization_complete"})
            
            # Handle resizing if specified
            if resize_options:
                image = _resize_image_smart(image, resize_options)
                self.update_state(state="PROCESSING", meta={"step": "resize_complete"})
            
            # Handle metadata
            metadata = {}
            if metadata_options and metadata_options.get("preserve_metadata", False):
                metadata = _extract_metadata(image)
            
            # Convert to target format
            converted_data = _convert_image_format(
                image, target_format, quality, optimization_level
            )
            
            self.update_state(state="PROCESSING", meta={"step": "conversion_complete"})
            
            # Calculate compression ratio
            compression_ratio = len(image_data) / len(converted_data) if converted_data else 1.0
            
            result = {
                "image_data": converted_data,
                "original_format": original_format,
                "target_format": target_format,
                "original_size": len(image_data),
                "converted_size": len(converted_data) if converted_data else 0,
                "compression_ratio": compression_ratio,
                "quality": quality,
                "optimization_level": optimization_level,
                "metadata": metadata,
                "success": True
            }
            
            return result
            
        finally:
            # Cleanup temporary file
            if os.path.exists(temp_input_path):
                os.unlink(temp_input_path)
    
    except Exception as exc:
        # Retry logic
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=exc)
        
        return {
            "success": False,
            "error": str(exc),
            "original_size": len(image_data),
            "target_format": target_format
        }


@celery_app.task(
    bind=True,
    name="app.tasks.image_tasks.batch_convert_images",
    max_retries=2
)
def batch_convert_images(
    self,
    images_data: List[Dict[str, Any]],
    conversion_settings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convert multiple images in batch with progress tracking.
    
    Args:
        images_data: List of image data dictionaries
        conversion_settings: Common conversion settings
    
    Returns:
        Dictionary with batch conversion results
    """
    results = []
    total_images = len(images_data)
    
    for i, image_info in enumerate(images_data):
        try:
            # Update progress
            progress = int((i / total_images) * 100)
            self.update_state(
                state="PROCESSING",
                meta={
                    "progress": progress,
                    "current": i + 1,
                    "total": total_images,
                    "current_file": image_info.get("filename", f"image_{i}")
                }
            )
            
            # Convert individual image
            result = convert_image_async.apply(
                args=[
                    image_info["data"],
                    conversion_settings["target_format"],
                    conversion_settings.get("quality", 85),
                    conversion_settings.get("optimization_level", "medium"),
                    conversion_settings.get("resize_options"),
                    conversion_settings.get("metadata_options")
                ]
            ).get()
            
            result["filename"] = image_info.get("filename", f"image_{i}")
            results.append(result)
            
        except Exception as e:
            results.append({
                "filename": image_info.get("filename", f"image_{i}"),
                "success": False,
                "error": str(e)
            })
    
    # Calculate batch statistics
    successful = sum(1 for r in results if r.get("success", False))
    failed = total_images - successful
    
    return {
        "results": results,
        "total_images": total_images,
        "successful": successful,
        "failed": failed,
        "success_rate": (successful / total_images) * 100 if total_images > 0 else 0
    }


@celery_app.task(name="app.tasks.image_tasks.optimize_image_async")
def optimize_image_async(
    image_data: bytes,
    optimization_type: str = "size",
    target_size_kb: Optional[int] = None,
    maintain_quality: bool = True
) -> Dict[str, Any]:
    """
    Optimize image for size or quality.
    
    Args:
        image_data: Raw image data
        optimization_type: "size", "quality", or "balanced"
        target_size_kb: Target file size in KB
        maintain_quality: Whether to maintain visual quality
    
    Returns:
        Optimized image data and statistics
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(image_data)
            temp_path = temp_file.name
        
        try:
            image, original_format = _load_image_optimized(temp_path)
            
            if optimization_type == "size":
                optimized_data = _optimize_for_size(image, target_size_kb, maintain_quality)
            elif optimization_type == "quality":
                optimized_data = _optimize_for_quality(image)
            else:  # balanced
                optimized_data = _optimize_balanced(image)
            
            compression_ratio = len(image_data) / len(optimized_data)
            
            return {
                "image_data": optimized_data,
                "original_size": len(image_data),
                "optimized_size": len(optimized_data),
                "compression_ratio": compression_ratio,
                "optimization_type": optimization_type,
                "success": True
            }
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "original_size": len(image_data)
        }


def _load_image_optimized(file_path: str) -> Tuple[Image.Image, str]:
    """Load image using the most appropriate method based on format."""
    try:
        # Try PIL first (fastest for most formats)
        with Image.open(file_path) as img:
            original_format = img.format or "UNKNOWN"
            
            # Handle RAW formats with rawpy
            if original_format.upper() in ["CR2", "NEF", "ARW", "DNG", "ORF", "RW2"]:
                return _load_raw_image(file_path), original_format
            
            # Load and convert if necessary
            img = img.copy()
            
            # Auto-rotate based on EXIF
            img = ImageOps.exif_transpose(img)
            
            return img, original_format
    
    except Exception:
        # Fallback to other loaders
        try:
            # Try with Wand (ImageMagick)
            with WandImage(filename=file_path) as img:
                img_format = img.format or "UNKNOWN"
                blob = img.make_blob(format='png')
                pil_img = Image.open(io.BytesIO(blob))
                return pil_img, img_format
        except Exception:
            # Final fallback
            raise ValueError(f"Unable to load image from {file_path}")


def _load_raw_image(file_path: str) -> Image.Image:
    """Load RAW image file using rawpy."""
    if not ADVANCED_LIBS.get('rawpy'):
        raise ValueError("RAW image support not available - rawpy not installed")
    
    import rawpy
    with rawpy.imread(file_path) as raw:
        rgb = raw.postprocess()
        return Image.fromarray(rgb)


def _apply_advanced_optimization(image: Image.Image, level: str) -> Image.Image:
    """Apply advanced optimization techniques."""
    if level == "maximum" and ADVANCED_LIBS.get('numpy') and ADVANCED_LIBS.get('skimage'):
        # Convert to numpy array for advanced processing
        import numpy as np
        img_array = np.array(image)
        
        # Apply noise reduction
        if len(img_array.shape) == 3:  # Color image
            # Use scikit-image for noise reduction
            from skimage import restoration
            img_array = restoration.denoise_tv_chambolle(img_array, weight=0.1)
            img_array = (img_array * 255).astype(np.uint8)
        
        # Convert back to PIL
        image = Image.fromarray(img_array)
        
        # Apply sharpening filter
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
    
    elif level in ["high", "maximum"]:
        # Apply moderate optimization (fallback)
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
    elif level == "medium":
        # Apply basic sharpening
        image = image.filter(ImageFilter.SHARPEN)
    
    return image


def _resize_image_smart(image: Image.Image, resize_options: Dict[str, Any]) -> Image.Image:
    """Smart image resizing with various options."""
    width = resize_options.get("width")
    height = resize_options.get("height")
    preset = resize_options.get("preset")
    maintain_aspect = resize_options.get("maintain_aspect", True)
    upscale = resize_options.get("upscale", False)
    
    original_width, original_height = image.size
    
    # Use preset if specified
    if preset and preset in SIZE_PRESETS:
        width, height = SIZE_PRESETS[preset]
    
    if not width and not height:
        return image
    
    # Calculate new dimensions
    if maintain_aspect:
        if width and height:
            # Fit within bounds
            image.thumbnail((width, height), Image.Resampling.LANCZOS)
        elif width:
            ratio = width / original_width
            if ratio > 1 and not upscale:
                return image
            height = int(original_height * ratio)
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        elif height:
            ratio = height / original_height
            if ratio > 1 and not upscale:
                return image
            width = int(original_width * ratio)
            image = image.resize((width, height), Image.Resampling.LANCZOS)
    else:
        # Exact dimensions (may distort)
        if not upscale and (width > original_width or height > original_height):
            return image
        image = image.resize((width, height), Image.Resampling.LANCZOS)
    
    return image


def _convert_image_format(
    image: Image.Image,
    target_format: str,
    quality: int,
    optimization_level: str
) -> bytes:
    """Convert image to target format with optimization."""
    output_buffer = io.BytesIO()
    
    # Normalize format
    target_format = target_format.lower()
    if target_format == "jpg":
        target_format = "jpeg"
    
    # Prepare image for target format
    if target_format == "jpeg" and image.mode in ("RGBA", "LA", "P"):
        # Convert to RGB for JPEG
        background = Image.new("RGB", image.size, (255, 255, 255))
        if image.mode == "P":
            image = image.convert("RGBA")
        if image.mode == "RGBA":
            background.paste(image, mask=image.split()[-1])
        image = background
    
    # Determine save parameters
    save_kwargs = {"format": target_format.upper()}
    
    if target_format == "jpeg":
        save_kwargs.update({
            "quality": quality,
            "optimize": True,
            "progressive": optimization_level in ["high", "maximum"],
            "subsampling": 0 if quality > 90 else 2
        })
    elif target_format == "png":
        save_kwargs.update({
            "optimize": True,
            "compress_level": 9 if optimization_level in ["high", "maximum"] else 6
        })
    elif target_format == "webp":
        save_kwargs.update({
            "quality": quality,
            "method": 6 if optimization_level in ["high", "maximum"] else 4,
            "lossless": quality == 100
        })
    elif target_format == "avif":
        save_kwargs.update({
            "quality": quality,
            "speed": 1 if optimization_level in ["high", "maximum"] else 6
        })
    elif target_format == "heic":
        save_kwargs.update({
            "quality": quality,
            "optimize": True
        })
    
    # Save image
    image.save(output_buffer, **save_kwargs)
    return output_buffer.getvalue()


def _extract_metadata(image: Image.Image) -> Dict[str, Any]:
    """Extract metadata from image."""
    metadata = {}
    
    # Basic image info
    metadata.update({
        "format": image.format,
        "mode": image.mode,
        "size": image.size,
        "has_transparency": image.mode in ("RGBA", "LA") or "transparency" in image.info
    })
    
    # EXIF data
    if hasattr(image, "_getexif") and image._getexif():
        exif = image._getexif()
        exif_data = {}
        for tag_id, value in exif.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            exif_data[tag] = value
        metadata["exif"] = exif_data
    
    return metadata


def _optimize_for_size(
    image: Image.Image,
    target_size_kb: Optional[int],
    maintain_quality: bool
) -> bytes:
    """Optimize image to achieve target file size."""
    if not target_size_kb:
        # Default optimization without size target
        return _convert_image_format(image, "jpeg", 85, "medium")
    
    target_bytes = target_size_kb * 1024
    quality = 95
    
    while quality > 10:
        test_data = _convert_image_format(image, "jpeg", quality, "medium")
        if len(test_data) <= target_bytes:
            return test_data
        quality -= 5
    
    # If still too large, try resizing
    scale = 0.9
    while scale > 0.3:
        resized = image.copy()
        new_size = (int(image.width * scale), int(image.height * scale))
        resized = resized.resize(new_size, Image.Resampling.LANCZOS)
        test_data = _convert_image_format(resized, "jpeg", 80, "medium")
        if len(test_data) <= target_bytes:
            return test_data
        scale -= 0.1
    
    # Final attempt with minimum quality
    return _convert_image_format(image, "jpeg", 30, "low")


def _optimize_for_quality(image: Image.Image) -> bytes:
    """Optimize image for maximum quality."""
    return _convert_image_format(image, "png", 100, "maximum")


def _optimize_balanced(image: Image.Image) -> bytes:
    """Optimize image with balanced size/quality."""
    return _convert_image_format(image, "webp", 90, "high")