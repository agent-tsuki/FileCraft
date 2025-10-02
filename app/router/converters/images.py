"""
Image conversion router using service layer.
"""
from fastapi import APIRouter, Depends, Form, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.schemas.responses import FileProcessingResponse
from app.services.image import ImageService, get_image_service

image_router = APIRouter(prefix="/images", tags=["Image Converter"])


@image_router.post(
    "/convert",
    response_model=FileProcessingResponse,
    summary="Convert image format",
    description="Convert image from one format to another with quality control"
)
async def convert_image_format(
    image: UploadFile,
    target_format: str = Form(..., description="Target format: jpeg, png, webp, bmp, gif, tiff"),
    quality: int = Query(default=85, ge=1, le=100, description="Image quality (1-100)"),
    image_service: ImageService = Depends(get_image_service)
) -> StreamingResponse:
    """
    Convert image to specified format.
    
    - **image**: Image file to convert
    - **target_format**: Target format (jpeg, png, webp, bmp, gif, tiff)  
    - **quality**: Image quality for lossy formats (1-100)
    
    Returns converted image as streaming response.
    """
    # Convert image
    converted_image = await image_service.convert_image_format(
        image, target_format, quality
    )
    
    # Generate filename
    original_filename = image.filename or "image"
    base_name = original_filename.rsplit(".", 1)[0] if "." in original_filename else original_filename
    output_filename = f"{base_name}.{target_format.lower()}"
    
    # Determine content type
    content_type = f"image/{target_format.lower()}"
    if target_format.lower() == "jpg":
        content_type = "image/jpeg"
    
    return StreamingResponse(
        converted_image,
        media_type=content_type,
        headers={
            "Content-Disposition": f"inline; filename={output_filename}"
        }
    )


# Keep backward compatibility
imageRouter = image_router

