"""
File compression router using service layer.
"""
import os

from fastapi import APIRouter, Depends, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.schemas.responses import FileProcessingResponse
from app.services.compression import CompressionService, get_compression_service

compression_router = APIRouter(prefix="/compression", tags=["File Compressor"])


@compression_router.post(
    "/smart-compress",
    response_model=FileProcessingResponse,
    summary="Smart file compression",
    description="Intelligently compress files and images with format-specific optimizations"
)
async def smart_compress_file(
    file: UploadFile,
    compression_level: int = Query(
        default=6, ge=1, le=9,
        description="Compression level for binary files (1-9)"
    ),
    quality: int = Query(
        default=70, ge=10, le=95,
        description="Image quality for lossy formats (10-95)"
    ),
    force_webp: bool = Query(
        default=False,
        description="Convert all images to WebP format"
    ),
    compression_service: CompressionService = Depends(get_compression_service)
) -> StreamingResponse:
    """
    Smart compression for files and images.
    
    - **file**: File to compress
    - **compression_level**: Compression level for binary files (1-9)
    - **quality**: Image quality for lossy formats (10-95)
    - **force_webp**: Convert all images to WebP format
    
    Returns compressed file as streaming response.
    """
    # Compress file
    compressed_file = await compression_service.smart_compress_file(
        file, compression_level, quality, force_webp
    )
    
    # Generate output filename
    original_filename = file.filename or "file"
    filename_base, ext = os.path.splitext(original_filename)
    ext = ext.lower().strip(".")
    
    # Determine output extension and media type
    image_extensions = {"jpg", "jpeg", "png", "webp", "tiff", "bmp", "gif"}
    
    if ext in image_extensions:
        if force_webp:
            output_filename = f"{filename_base}_compressed.webp"
            media_type = "image/webp"
        else:
            target_ext = "jpeg" if ext == "jpg" else ext
            output_filename = f"{filename_base}_compressed.{target_ext}"
            media_type = f"image/{target_ext}"
    else:
        # Binary file
        output_filename = f"{filename_base}_compressed.wxct"
        media_type = "application/octet-stream"
    
    return StreamingResponse(
        compressed_file,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={output_filename}"
        }
    )


# Keep backward compatibility
router = compression_router
