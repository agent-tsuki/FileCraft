"""
Optimization and utility tasks for image processing.
"""

import os
import io
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, TYPE_CHECKING
import logging

from app.celery_app import celery_app

if TYPE_CHECKING:
    from PIL import Image

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.optimization_tasks.cleanup_temp_files")
def cleanup_temp_files() -> Dict[str, Any]:
    """
    Clean up temporary files older than 1 hour.

    Returns:
        Dictionary with cleanup statistics
    """
    try:
        temp_dir = tempfile.gettempdir()
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=1)

        cleaned_files = 0
        cleaned_size = 0
        errors = []

        for filename in os.listdir(temp_dir):
            if filename.startswith("tmp") and (
                filename.endswith(".jpg")
                or filename.endswith(".png")
                or filename.endswith(".webp")
            ):
                file_path = os.path.join(temp_dir, filename)
                try:
                    # Check file modification time
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if mod_time < cutoff_time:
                        file_size = os.path.getsize(file_path)
                        os.unlink(file_path)
                        cleaned_files += 1
                        cleaned_size += file_size
                except Exception as e:
                    errors.append(f"Error cleaning {filename}: {str(e)}")

        logger.info(f"Cleanup completed: {cleaned_files} files, {cleaned_size} bytes")

        return {
            "success": True,
            "cleaned_files": cleaned_files,
            "cleaned_size": cleaned_size,
            "errors": errors,
            "timestamp": current_time.isoformat(),
        }

    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@celery_app.task(name="app.tasks.optimization_tasks.generate_thumbnails")
def generate_thumbnails(image_data: bytes, sizes: List[tuple] = None) -> Dict[str, Any]:
    """
    Generate multiple thumbnail sizes for an image.

    Args:
        image_data: Raw image data
        sizes: List of (width, height) tuples

    Returns:
        Dictionary with thumbnail data for each size
    """
    if sizes is None:
        sizes = [(150, 150), (300, 300), (600, 600)]

    try:
        from PIL import Image

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(image_data)
            temp_path = temp_file.name

        try:
            thumbnails = {}

            with Image.open(temp_path) as img:
                for size in sizes:
                    # Create thumbnail
                    thumb = img.copy()
                    thumb.thumbnail(size, Image.Resampling.LANCZOS)

                    # Save to bytes
                    thumb_buffer = io.BytesIO()
                    thumb.save(thumb_buffer, format="JPEG", quality=85, optimize=True)

                    size_key = f"{size[0]}x{size[1]}"
                    thumbnails[size_key] = {
                        "data": thumb_buffer.getvalue(),
                        "size": thumb.size,
                        "file_size": len(thumb_buffer.getvalue()),
                    }

            return {
                "success": True,
                "thumbnails": thumbnails,
                "original_size": len(image_data),
            }

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except Exception as e:
        return {"success": False, "error": str(e)}


@celery_app.task(name="app.tasks.optimization_tasks.analyze_image_stats")
def analyze_image_stats(image_data: bytes) -> Dict[str, Any]:
    """
    Analyze image statistics and properties.

    Args:
        image_data: Raw image data

    Returns:
        Dictionary with comprehensive image analysis
    """
    try:
        from PIL import Image
        import io

        with Image.open(io.BytesIO(image_data)) as img:
            # Basic properties
            stats = {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height,
                "file_size": len(image_data),
                "aspect_ratio": img.width / img.height,
                "megapixels": (img.width * img.height) / 1000000,
                "color_depth": len(img.getbands()),
                "has_transparency": img.mode in ("RGBA", "LA")
                or "transparency" in img.info,
            }

            # Color analysis for RGB images
            if img.mode in ("RGB", "RGBA"):
                # Convert to RGB if needed
                if img.mode == "RGBA":
                    # Create white background
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    rgb_img = background
                else:
                    rgb_img = img

                # Calculate color statistics
                try:
                    import numpy as np

                    img_array = np.array(rgb_img)

                    stats["color_stats"] = {
                        "mean_rgb": img_array.mean(axis=(0, 1)).tolist(),
                        "std_rgb": img_array.std(axis=(0, 1)).tolist(),
                        "brightness": float(img_array.mean()),
                        "contrast": float(img_array.std()),
                    }
                except ImportError:
                    # Fallback without numpy
                    stats["color_stats"] = {
                        "note": "Advanced color analysis unavailable"
                    }

            # Compression efficiency estimate
            if img.format == "JPEG":
                stats["compression_quality"] = _estimate_jpeg_quality(img)

            return {"success": True, "stats": stats}

    except Exception as e:
        return {"success": False, "error": str(e)}


def _estimate_jpeg_quality(img: "Image.Image") -> Dict[str, Any]:
    """Estimate JPEG quality and compression artifacts."""
    try:
        # This is a simplified estimation
        # In practice, you'd analyze DCT coefficients for accurate quality estimation
        file_size_per_pixel = len(img.tobytes()) / (img.width * img.height)

        if file_size_per_pixel > 3:
            estimated_quality = "High (90-100)"
        elif file_size_per_pixel > 2:
            estimated_quality = "Medium-High (75-90)"
        elif file_size_per_pixel > 1:
            estimated_quality = "Medium (60-75)"
        elif file_size_per_pixel > 0.5:
            estimated_quality = "Low-Medium (40-60)"
        else:
            estimated_quality = "Low (0-40)"

        return {
            "estimated_quality": estimated_quality,
            "size_per_pixel": file_size_per_pixel,
            "compression_artifacts": "Low" if file_size_per_pixel > 2 else "Possible",
        }

    except Exception:
        return {"note": "Quality estimation failed"}


@celery_app.task(name="app.tasks.optimization_tasks.watermark_image")
def watermark_image(
    image_data: bytes,
    watermark_text: str = None,
    watermark_image_data: bytes = None,
    position: str = "bottom-right",
    opacity: float = 0.5,
) -> Dict[str, Any]:
    """
    Add watermark to image.

    Args:
        image_data: Original image data
        watermark_text: Text watermark
        watermark_image_data: Image watermark data
        position: Watermark position
        opacity: Watermark opacity (0-1)

    Returns:
        Watermarked image data
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io

        with Image.open(io.BytesIO(image_data)) as img:
            # Create a copy
            watermarked = img.copy()

            if watermark_text:
                # Text watermark
                draw = ImageDraw.Draw(watermarked)

                # Try to load a font, fallback to default
                try:
                    font_size = max(20, min(img.width, img.height) // 20)
                    font = ImageFont.truetype("arial.ttf", font_size)
                except (OSError, ImportError):
                    font = ImageFont.load_default()

                # Calculate text position
                bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                # Position mapping
                positions = {
                    "top-left": (10, 10),
                    "top-right": (img.width - text_width - 10, 10),
                    "bottom-left": (10, img.height - text_height - 10),
                    "bottom-right": (
                        img.width - text_width - 10,
                        img.height - text_height - 10,
                    ),
                    "center": (
                        (img.width - text_width) // 2,
                        (img.height - text_height) // 2,
                    ),
                }

                text_pos = positions.get(position, positions["bottom-right"])

                # Draw text with transparency
                text_color = (255, 255, 255, int(255 * opacity))
                draw.text(text_pos, watermark_text, fill=text_color, font=font)

            elif watermark_image_data:
                # Image watermark
                with Image.open(io.BytesIO(watermark_image_data)) as watermark:
                    # Resize watermark if too large
                    max_size = min(img.width // 4, img.height // 4)
                    if watermark.width > max_size or watermark.height > max_size:
                        watermark.thumbnail(
                            (max_size, max_size), Image.Resampling.LANCZOS
                        )

                    # Apply opacity
                    if watermark.mode != "RGBA":
                        watermark = watermark.convert("RGBA")

                    # Adjust opacity
                    alpha = watermark.split()[-1]
                    alpha = alpha.point(lambda p: int(p * opacity))
                    watermark.putalpha(alpha)

                    # Calculate position
                    positions = {
                        "top-left": (10, 10),
                        "top-right": (img.width - watermark.width - 10, 10),
                        "bottom-left": (10, img.height - watermark.height - 10),
                        "bottom-right": (
                            img.width - watermark.width - 10,
                            img.height - watermark.height - 10,
                        ),
                        "center": (
                            (img.width - watermark.width) // 2,
                            (img.height - watermark.height) // 2,
                        ),
                    }

                    wm_pos = positions.get(position, positions["bottom-right"])

                    # Paste watermark
                    watermarked.paste(watermark, wm_pos, watermark)

            # Save result
            output_buffer = io.BytesIO()
            watermarked.save(
                output_buffer, format=img.format or "JPEG", quality=90, optimize=True
            )

            return {
                "success": True,
                "watermarked_data": output_buffer.getvalue(),
                "original_size": len(image_data),
                "watermarked_size": len(output_buffer.getvalue()),
            }

    except Exception as e:
        return {"success": False, "error": str(e)}
