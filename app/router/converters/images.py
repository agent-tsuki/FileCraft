"""
Enhanced image conversion router with comprehensive format support and advanced features.
"""
from typing import List, Optional, Dict, Any, Union
from fastapi import APIRouter, Depends, Form, Query, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from enum import Enum

from app.schemas.responses import FileProcessingResponse
from app.services.image import ImageService, get_image_service
from app.helpers.constants import (
    SUPPORTED_OUTPUT_FORMATS, QUALITY_PRESETS, SIZE_PRESETS, IMAGE_FORMATS
)

image_router = APIRouter(prefix="/images", tags=["Image Converter"])


class ImageFormat(str, Enum):
    """Supported image output formats."""
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    WEBP = "webp"
    BMP = "bmp"
    GIF = "gif"
    TIFF = "tiff"
    TIF = "tif"
    AVIF = "avif"
    HEIC = "heic"
    HEIF = "heif"
    ICO = "ico"
    JP2 = "jp2"
    PDF = "pdf"


class QualityPreset(str, Enum):
    """Quality presets for easy selection."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"
    LOSSLESS = "lossless"


class SizePreset(str, Enum):
    """Size presets for common dimensions."""
    THUMBNAIL = "thumbnail"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HD = "hd"
    FULL_HD = "full_hd"
    K2 = "2k"
    K4 = "4k"
    K8 = "8k"


class OptimizationLevel(str, Enum):
    """Optimization levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


@image_router.get("/formats", summary="Get supported image formats")
async def get_supported_formats() -> Dict[str, Any]:
    """
    Get list of all supported image formats with their capabilities.
    
    Returns detailed information about each supported format including:
    - Format name and description
    - Year introduced
    - Whether it supports transparency, animation, lossless compression
    """
    return {
        "input_formats": {
            format_code: {
                "name": info["name"],
                "year": info["year"],
                "lossy": info["lossy"],
                "transparency": info["transparency"],
                "animation": info["animation"]
            }
            for format_code, info in IMAGE_FORMATS.items()
        },
        "output_formats": SUPPORTED_OUTPUT_FORMATS,
        "quality_presets": QUALITY_PRESETS,
        "size_presets": SIZE_PRESETS
    }


@image_router.post(
    "/convert",
    summary="Convert image format with advanced options",
    description="Convert image from one format to another with comprehensive customization options",
    response_model=None
)
async def convert_image_format(
    image: UploadFile = File(..., description="Image file to convert"),
    target_format: ImageFormat = Form(..., description="Target format for conversion"),
    quality: Optional[int] = Query(
        default=85, 
        ge=1, 
        le=100, 
        description="Image quality (1-100, only for lossy formats)"
    ),
    quality_preset: Optional[QualityPreset] = Query(
        default=None, 
        description="Quality preset (overrides quality if specified)"
    ),
    optimization_level: OptimizationLevel = Query(
        default=OptimizationLevel.MEDIUM,
        description="Optimization level for processing"
    ),
    use_async: bool = Query(
        default=False,
        description="Use background processing (returns task ID)"
    ),
    # Resize options
    resize_width: Optional[int] = Query(
        default=None, 
        ge=1, 
        le=8000,
        description="Target width in pixels"
    ),
    resize_height: Optional[int] = Query(
        default=None, 
        ge=1, 
        le=8000,
        description="Target height in pixels"
    ),
    size_preset: Optional[SizePreset] = Query(
        default=None,
        description="Size preset (overrides width/height if specified)"
    ),
    maintain_aspect_ratio: bool = Query(
        default=True,
        description="Maintain aspect ratio when resizing"
    ),
    allow_upscale: bool = Query(
        default=False,
        description="Allow upscaling (enlarging) images"
    ),
    image_service: ImageService = Depends(get_image_service)
) -> Union[StreamingResponse, JSONResponse]:
    """
    Convert image to specified format with advanced options.
    
    **Features:**
    - Support for 14+ output formats (JPEG, PNG, WebP, AVIF, HEIC, etc.)
    - Quality presets and custom quality settings
    - Image resizing with aspect ratio preservation
    - Multiple optimization levels
    - Background processing for large files
    
    **Parameters:**
    - **image**: Image file to convert (supports 20+ input formats)
    - **target_format**: Output format from dropdown
    - **quality**: Custom quality (1-100) or use preset
    - **optimization_level**: Processing optimization level
    - **resize options**: Width, height, or preset sizes
    - **use_async**: Background processing for large files
    
    **Returns:**
    - Synchronous: Converted image as streaming response
    - Asynchronous: JSON with task ID for status checking
    """
    # Use quality preset if specified
    if quality_preset:
        quality = QUALITY_PRESETS[quality_preset.value]
    
    # Prepare resize options
    resize_options = None
    if resize_width or resize_height or size_preset:
        resize_options = {
            "width": resize_width,
            "height": resize_height,
            "preset": size_preset.value if size_preset else None,
            "maintain_aspect": maintain_aspect_ratio,
            "upscale": allow_upscale
        }
    
    # Convert image
    result = await image_service.convert_image_format(
        image, 
        target_format.value, 
        quality,
        use_async,
        resize_options,
        optimization_level.value
    )
    
    # Handle async response
    if isinstance(result, dict) and "task_id" in result:
        return JSONResponse(content=result)
    
    # Handle sync response
    original_filename = image.filename or "image"
    base_name = original_filename.rsplit(".", 1)[0] if "." in original_filename else original_filename
    output_filename = f"{base_name}.{target_format.value}"
    
    # Determine content type
    content_type = f"image/{target_format.value}"
    if target_format.value in ["jpg", "jpeg"]:
        content_type = "image/jpeg"
    
    return StreamingResponse(
        result,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={output_filename}",
            "X-Original-Format": image.content_type or "unknown",
            "X-Target-Format": target_format.value,
            "X-Quality": str(quality),
            "X-Optimization-Level": optimization_level.value
        }
    )


@image_router.post(
    "/batch-convert",
    summary="Batch convert multiple images",
    description="Convert multiple images at once with same settings"
)
async def batch_convert_images(
    images: List[UploadFile] = File(..., description="List of image files to convert"),
    target_format: ImageFormat = Form(..., description="Target format for all images"),
    quality: int = Query(default=85, ge=1, le=100, description="Image quality (1-100)"),
    optimization_level: OptimizationLevel = Query(
        default=OptimizationLevel.MEDIUM,
        description="Optimization level"
    ),
    image_service: ImageService = Depends(get_image_service)
) -> JSONResponse:
    """
    Convert multiple images in batch with progress tracking.
    
    **Features:**
    - Process multiple images with same settings
    - Background processing with progress tracking
    - Detailed results for each image
    
    Returns task ID for tracking batch conversion progress.
    """
    result = await image_service.batch_convert_images(
        images, target_format.value, quality, optimization_level.value
    )
    
    return JSONResponse(content=result)


@image_router.post(
    "/optimize",
    summary="Optimize image size and quality",
    description="Optimize image for specific use case (size, quality, or balanced)",
    response_model=None
)
async def optimize_image(
    image: UploadFile = File(..., description="Image file to optimize"),
    optimization_type: str = Query(
        default="balanced",
        regex="^(size|quality|balanced)$",
        description="Optimization type: size, quality, or balanced"
    ),
    target_size_kb: Optional[int] = Query(
        default=None,
        ge=10,
        le=10240,
        description="Target file size in KB (for size optimization)"
    ),
    image_service: ImageService = Depends(get_image_service)
) -> Union[StreamingResponse, JSONResponse]:
    """
    Optimize image for specific requirements.
    
    **Optimization Types:**
    - **size**: Minimize file size (optionally to target KB)
    - **quality**: Maximize visual quality
    - **balanced**: Balance between size and quality
    
    Returns optimized image or task ID for background processing.
    """
    result = await image_service.optimize_image(
        image, optimization_type, target_size_kb
    )
    
    if isinstance(result, dict) and "task_id" in result:
        return JSONResponse(content=result)
    
    original_filename = image.filename or "image"
    base_name = original_filename.rsplit(".", 1)[0] if "." in original_filename else original_filename
    output_filename = f"{base_name}_optimized.webp"
    
    return StreamingResponse(
        result,
        media_type="image/webp",
        headers={
            "Content-Disposition": f"attachment; filename={output_filename}",
            "X-Optimization-Type": optimization_type,
            "X-Target-Size-KB": str(target_size_kb) if target_size_kb else "auto"
        }
    )


@image_router.post(
    "/info",
    summary="Get image information and analysis",
    description="Analyze image properties, format, and metadata"
)
async def get_image_info(
    image: UploadFile = File(..., description="Image file to analyze"),
    image_service: ImageService = Depends(get_image_service)
) -> JSONResponse:
    """
    Get comprehensive image information and analysis.
    
    **Analysis includes:**
    - Format and technical properties
    - Dimensions and file size
    - Color information
    - Compression quality estimation
    - Format recommendations
    
    Returns detailed image analysis data.
    """
    result = await image_service.get_image_info(image)
    return JSONResponse(content=result)


@image_router.get(
    "/task/{task_id}",
    summary="Get task status",
    description="Check status of background image processing task"
)
async def get_task_status(task_id: str) -> JSONResponse:
    """
    Get the status of a background processing task.
    
    **Status values:**
    - **PENDING**: Task is waiting to be processed
    - **PROCESSING**: Task is currently being processed
    - **SUCCESS**: Task completed successfully
    - **FAILURE**: Task failed with error
    
    Returns task status and result data if completed.
    """
    try:
        from app.celery_app import celery_app
        
        task = celery_app.AsyncResult(task_id)
        
        if task.state == "PENDING":
            response = {
                "task_id": task_id,
                "status": "PENDING",
                "message": "Task is waiting to be processed"
            }
        elif task.state == "PROCESSING":
            response = {
                "task_id": task_id,
                "status": "PROCESSING",
                "progress": task.info.get("progress", 0),
                "step": task.info.get("step", "unknown")
            }
        elif task.state == "SUCCESS":
            response = {
                "task_id": task_id,
                "status": "SUCCESS",
                "result": task.result
            }
        else:  # FAILURE
            response = {
                "task_id": task_id,
                "status": "FAILURE",
                "error": str(task.info)
            }
        
        return JSONResponse(content=response)
    
    except ImportError:
        return JSONResponse(
            content={
                "error": "Celery not available",
                "message": "Background task processing is not configured"
            },
            status_code=503
        )


# Keep backward compatibility
imageRouter = image_router

