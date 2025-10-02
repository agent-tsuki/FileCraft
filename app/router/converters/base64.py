"""
Base64 conversion router using service layer.
"""
from fastapi import APIRouter, Depends, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.schemas.responses import FileProcessingResponse
from app.services.base64 import Base64Service, get_base64_service

base64_router = APIRouter(prefix="/base64", tags=["Base64 Converter"])


@base64_router.post(
    "/file",
    response_model=FileProcessingResponse,
    summary="Convert file to Base64",
    description="Convert any uploaded file to Base64 encoding with optional compression"
)
async def convert_file_to_base64(
    file: UploadFile,
    compress: bool = Query(default=False, description="Compress file before encoding"),
    base64_service: Base64Service = Depends(get_base64_service)
) -> StreamingResponse:
    """
    Convert uploaded file to Base64 format.
    
    - **file**: File to be converted
    - **compress**: Whether to compress the file before encoding (optional)
    
    Returns a streaming response with Base64 encoded content.
    """
    # Generate base64 stream
    base64_stream = base64_service.convert_to_base64_stream(file, compress)
    
    # Generate filename
    original_filename = file.filename or "unknown"
    output_filename = f"{original_filename}.b64"
    
    return StreamingResponse(
        base64_stream,
        media_type="text/plain",
        headers={
            "Content-Disposition": f"inline; filename={output_filename}"
        }
    )


# Keep backward compatibility
base64Router = base64_router
