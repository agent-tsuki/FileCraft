"""
Base64 decoder router.
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional

from app.services.decoders.base64_decoder import Base64DecoderService, get_base64_decoder_service

base64_decoder_router = APIRouter(prefix="/decode/base64", tags=["Base64 Decoder"])


@base64_decoder_router.post(
    "/file",
    summary="Decode Base64 file",
    description="Decode a file containing Base64 encoded data"
)
async def decode_base64_file(
    file: UploadFile = File(...),
    url_safe: Optional[bool] = Query(default=None, description="Force URL-safe decoding (auto-detect if None)"),
    validate: bool = Query(default=True, description="Validate Base64 format"),
    return_stream: bool = Query(default=False, description="Return as streaming response"),
    service: Base64DecoderService = Depends(get_base64_decoder_service)
) -> StreamingResponse:
    """
    Decode Base64 file content.
    
    - **file**: File containing Base64 data to decode
    - **url_safe**: Force URL-safe decoding (auto-detect if not specified)
    - **validate**: Validate Base64 format before decoding
    - **return_stream**: Return as streaming response
    
    Returns decoded binary content.
    """
    try:
        if return_stream:
            # Return as streaming response
            decoded_stream = service.decode_stream(file, url_safe=url_safe, validate=validate)
            output_filename = service.get_output_filename(file.filename or "unknown")
            
            return StreamingResponse(
                decoded_stream,
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f"attachment; filename={output_filename}"
                }
            )
        else:
            # Return as direct response
            decoded_content = await service.decode_file(file, url_safe=url_safe, validate=validate)
            output_filename = service.get_output_filename(file.filename or "unknown")
            
            return StreamingResponse(
                iter([decoded_content]),
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f"attachment; filename={output_filename}"
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decoding failed: {str(e)}")


@base64_decoder_router.post(
    "/text",
    summary="Decode Base64 text",
    description="Decode Base64 encoded text string"
)
async def decode_base64_text(
    encoded_text: str = Form(..., description="Base64 encoded text to decode"),
    url_safe: Optional[bool] = Query(default=None, description="Force URL-safe decoding (auto-detect if None)"),
    validate: bool = Query(default=True, description="Validate Base64 format"),
    output_format: str = Query(default="text", enum=["text", "hex", "binary"], description="Output format"),
    encoding: str = Query(default="utf-8", description="Text encoding for text output"),
    service: Base64DecoderService = Depends(get_base64_decoder_service)
) -> JSONResponse:
    """
    Decode Base64 text.
    
    - **encoded_text**: Base64 encoded text to decode
    - **url_safe**: Force URL-safe decoding (auto-detect if not specified)
    - **validate**: Validate Base64 format before decoding
    - **output_format**: Output format (text, hex, binary)
    - **encoding**: Text encoding for text output
    
    Returns decoded content in requested format.
    """
    try:
        decoded_bytes = await service.decode(encoded_text, url_safe=url_safe, validate=validate)
        
        result = {
            "input": encoded_text[:100] + "..." if len(encoded_text) > 100 else encoded_text,
            "input_length": len(encoded_text),
            "decoded_size": len(decoded_bytes),
            "url_safe_detected": service._is_url_safe_base64(encoded_text.replace(" ", ""))
        }
        
        if output_format == "text":
            try:
                result["decoded"] = decoded_bytes.decode(encoding)
                result["encoding"] = encoding
            except UnicodeDecodeError:
                result["decoded"] = "<Binary data cannot be displayed as text>"
                result["encoding"] = f"{encoding} (failed)"
        elif output_format == "hex":
            result["decoded"] = decoded_bytes.hex()
        elif output_format == "binary":
            result["decoded"] = list(decoded_bytes)
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decoding failed: {str(e)}")


@base64_decoder_router.post(
    "/validate",
    summary="Validate Base64 format",
    description="Validate if text is valid Base64 format"
)
async def validate_base64(
    encoded_text: str = Form(..., description="Text to validate"),
    service: Base64DecoderService = Depends(get_base64_decoder_service)
) -> JSONResponse:
    """
    Validate Base64 format.
    
    - **encoded_text**: Text to validate
    
    Returns validation results.
    """
    cleaned_text = ''.join(encoded_text.split())
    
    result = {
        "input": encoded_text[:100] + "..." if len(encoded_text) > 100 else encoded_text,
        "cleaned_length": len(cleaned_text),
        "is_valid": service._is_valid_base64(cleaned_text),
        "is_url_safe": service._is_url_safe_base64(cleaned_text),
        "has_padding": cleaned_text.endswith('='),
        "padding_correct": len(cleaned_text) % 4 == 0,
        "can_decode": False
    }
    
    # Try to decode to check if it's valid
    try:
        await service.decode(encoded_text, validate=False)
        result["can_decode"] = True
    except:
        result["can_decode"] = False
    
    return JSONResponse(content=result)


@base64_decoder_router.get(
    "/info", 
    summary="Get Base64 decoder information",
    description="Get information about Base64 decoding"
)
async def get_base64_decoder_info(
    service: Base64DecoderService = Depends(get_base64_decoder_service)
) -> JSONResponse:
    """
    Get Base64 decoder information.
    
    Returns information about Base64 decoding capabilities.
    """
    return JSONResponse(content={
        "decoder": "Base64",
        "description": "Base64 decoding converts ASCII text back to binary data",
        "formats_supported": {
            "standard": "Standard Base64 (RFC 4648) with + and / characters", 
            "url_safe": "URL-safe Base64 (RFC 4648) with - and _ characters",
            "auto_detect": "Automatic detection of standard vs URL-safe"
        },
        "features": [
            "Automatic padding correction",
            "Whitespace and separator removal",
            "Format validation",
            "Auto-detection of URL-safe encoding",
            "Multiple output formats"
        ],
        "parameters": {
            "url_safe": {
                "type": "boolean or null",
                "default": None,
                "description": "Force URL-safe decoding or auto-detect"
            },
            "validate": {
                "type": "boolean", 
                "default": True,
                "description": "Validate Base64 format before decoding"
            },
            "output_format": {
                "type": "string",
                "default": "text",
                "options": ["text", "hex", "binary"]
            }
        }
    })