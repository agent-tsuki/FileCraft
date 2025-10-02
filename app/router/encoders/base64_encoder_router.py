"""
Base64 encoder router.
"""

from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional, Dict, Any

from app.services.encoders.base64_encoder import (
    Base64EncoderService,
    get_base64_encoder_service,
)

base64_encoder_router = APIRouter(prefix="/encode/base64", tags=["Base64 Encoder"])


@base64_encoder_router.post(
    "/file",
    summary="Encode file to Base64",
    description="Convert any uploaded file to Base64 encoding",
)
async def encode_file_to_base64(
    file: UploadFile = File(...),
    url_safe: bool = Query(default=False, description="Use URL-safe Base64 encoding"),
    return_stream: bool = Query(
        default=False, description="Return as streaming response"
    ),
    service: Base64EncoderService = Depends(get_base64_encoder_service),
) -> StreamingResponse:
    """
    Encode uploaded file to Base64 format.

    - **file**: File to be encoded
    - **url_safe**: Whether to use URL-safe Base64 encoding
    - **return_stream**: Whether to return as streaming response

    Returns Base64 encoded content.
    """
    if return_stream:
        # Return as streaming response
        base64_stream = service.encode_stream(file, url_safe=url_safe)
        output_filename = service.get_output_filename(
            file.filename or "unknown", url_safe=url_safe
        )

        return StreamingResponse(
            base64_stream,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"},
        )
    else:
        # Return as direct response
        encoded_content = await service.encode_file(file, url_safe=url_safe)
        output_filename = service.get_output_filename(
            file.filename or "unknown", url_safe=url_safe
        )

        return StreamingResponse(
            iter([encoded_content.encode("utf-8")]),
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"},
        )


@base64_encoder_router.post(
    "/text",
    summary="Encode text to Base64",
    description="Convert text string to Base64 encoding",
)
async def encode_text_to_base64(
    text: str = Form(..., description="Text to encode"),
    url_safe: bool = Query(default=False, description="Use URL-safe Base64 encoding"),
    service: Base64EncoderService = Depends(get_base64_encoder_service),
) -> JSONResponse:
    """
    Encode text to Base64 format.

    - **text**: Text to be encoded
    - **url_safe**: Whether to use URL-safe Base64 encoding

    Returns Base64 encoded text.
    """
    encoded_text = await service.encode(text, url_safe=url_safe)

    return JSONResponse(
        content={
            "input": text,
            "encoded": encoded_text,
            "url_safe": url_safe,
            "algorithm": "base64_url" if url_safe else "base64",
        }
    )


@base64_encoder_router.get(
    "/info",
    summary="Get Base64 encoder information",
    description="Get information about Base64 encoding",
)
async def get_base64_encoder_info(
    service: Base64EncoderService = Depends(get_base64_encoder_service),
) -> JSONResponse:
    """
    Get Base64 encoder information.

    Returns information about Base64 encoding capabilities.
    """
    return JSONResponse(
        content={
            "encoder": "Base64",
            "description": "Base64 encoding converts binary data to ASCII text",
            "formats": {
                "standard": "Standard Base64 (RFC 4648) with + and / characters",
                "url_safe": "URL-safe Base64 (RFC 4648) with - and _ characters",
            },
            "use_cases": [
                "Encoding binary files for text transmission",
                "Embedding images in HTML/CSS",
                "API data serialization",
                "Email attachments (MIME)",
            ],
            "parameters": {
                "url_safe": {
                    "type": "boolean",
                    "default": False,
                    "description": "Use URL-safe encoding",
                }
            },
        }
    )
