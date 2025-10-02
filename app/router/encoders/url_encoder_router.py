"""
URL encoder router.
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional, Dict, Any

from app.services.encoders.url_encoder import URLEncoderService, get_url_encoder_service

url_encoder_router = APIRouter(prefix="/encode/url", tags=["URL Encoder"])


@url_encoder_router.post(
    "/text",
    summary="Encode text for URL",
    description="URL encode text string for safe transmission in URLs"
)
async def encode_text_to_url(
    text: str = Form(..., description="Text to URL encode"),
    safe: str = Query(default="", description="Characters to not encode"),
    encoding: str = Query(default="utf-8", description="Character encoding"),
    plus_encoding: bool = Query(default=False, description="Use + for spaces (quote_plus)"),
    service: URLEncoderService = Depends(get_url_encoder_service)
) -> JSONResponse:
    """
    URL encode text string.
    
    - **text**: Text to be URL encoded
    - **safe**: Characters that should not be encoded
    - **encoding**: Character encoding to use
    - **plus_encoding**: Use + for spaces instead of %20
    
    Returns URL encoded text.
    """
    try:
        if plus_encoding:
            encoded_text = service.encode_plus(text, safe=safe, encoding=encoding)
        else:
            encoded_text = await service.encode(text, safe=safe, encoding=encoding)
        
        return JSONResponse(content={
            "input": text,
            "encoded": encoded_text,
            "encoding": encoding,
            "safe_chars": safe,
            "plus_encoding": plus_encoding,
            "length_original": len(text),
            "length_encoded": len(encoded_text)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL encoding failed: {str(e)}")


@url_encoder_router.post(
    "/file",
    summary="Encode file content for URL",
    description="URL encode file content"
)
async def encode_file_to_url(
    file: UploadFile = File(...),
    safe: str = Query(default="", description="Characters to not encode"),
    encoding: str = Query(default="utf-8", description="Character encoding"),
    service: URLEncoderService = Depends(get_url_encoder_service)
) -> StreamingResponse:
    """
    URL encode file content.
    
    - **file**: File to be URL encoded
    - **safe**: Characters that should not be encoded
    - **encoding**: Character encoding to use
    
    Returns URL encoded file content.
    """
    try:
        encoded_content = await service.encode_file(file, safe=safe, encoding=encoding)
        output_filename = service.get_output_filename(file.filename or "unknown")
        
        return StreamingResponse(
            iter([encoded_content.encode('utf-8')]),
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL encoding failed: {str(e)}")


@url_encoder_router.post(
    "/params",
    summary="Encode dictionary as URL parameters",
    description="Convert dictionary to URL encoded query parameters"
)
async def encode_params_to_url(
    params: str = Form(..., description="JSON dictionary of parameters"),
    doseq: bool = Query(default=False, description="Handle sequences in values"),
    safe: str = Query(default="", description="Characters to not encode"),
    encoding: str = Query(default="utf-8", description="Character encoding"),
    service: URLEncoderService = Depends(get_url_encoder_service)
) -> JSONResponse:
    """
    Encode dictionary as URL query parameters.
    
    - **params**: JSON dictionary of parameters to encode
    - **doseq**: Handle sequences (lists) in parameter values
    - **safe**: Characters that should not be encoded
    - **encoding**: Character encoding to use
    
    Returns URL encoded query string.
    """
    try:
        import json
        
        # Parse JSON parameters
        try:
            param_dict = json.loads(params)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON parameters")
        
        if not isinstance(param_dict, dict):
            raise HTTPException(status_code=400, detail="Parameters must be a JSON object")
        
        encoded_params = service.encode_query_params(
            param_dict, 
            doseq=doseq, 
            safe=safe, 
            encoding=encoding
        )
        
        return JSONResponse(content={
            "input_params": param_dict,
            "encoded_query": encoded_params,
            "full_url_example": f"https://example.com/api?{encoded_params}",
            "encoding": encoding,
            "doseq": doseq,
            "param_count": len(param_dict)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parameter encoding failed: {str(e)}")


@url_encoder_router.post(
    "/component",
    summary="Encode URL component",
    description="Encode specific URL component (path, query, fragment)"
)
async def encode_url_component(
    component: str = Form(..., description="URL component to encode"),
    component_type: str = Query(default="query", enum=["path", "query", "fragment"], description="Type of URL component"),
    service: URLEncoderService = Depends(get_url_encoder_service)
) -> JSONResponse:
    """
    Encode specific URL component with appropriate safe characters.
    
    - **component**: URL component to encode
    - **component_type**: Type of component (affects safe characters)
    
    Returns encoded URL component.
    """
    try:
        # Set safe characters based on component type
        safe_chars = {
            "path": "/",  # Allow forward slashes in paths
            "query": "=&",  # Allow = and & in query strings
            "fragment": ""  # No safe chars for fragments
        }
        
        safe = safe_chars.get(component_type, "")
        encoded_component = await service.encode(component, safe=safe)
        
        return JSONResponse(content={
            "input": component,
            "encoded": encoded_component,
            "component_type": component_type,
            "safe_chars": safe,
            "use_case": {
                "path": "URL path segments",
                "query": "Query parameter names/values", 
                "fragment": "URL fragments (after #)"
            }[component_type]
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Component encoding failed: {str(e)}")


@url_encoder_router.get(
    "/chars",
    summary="Get URL encoding information",
    description="Get information about URL encoding and reserved characters"
)
async def get_url_encoding_chars() -> JSONResponse:
    """
    Get URL encoding character information.
    
    Returns information about URL encoding and character handling.
    """
    return JSONResponse(content={
        "reserved_chars": {
            "general": "! # $ & ' ( ) * + , / : ; = ? @ [ ]",
            "sub_delims": "! $ & ' ( ) * + , ; =",
            "gen_delims": ": / ? # [ ] @"
        },
        "percent_encoding": {
            "format": "%XX where XX is hexadecimal",
            "space": "%20 (or + in query strings)",
            "examples": {
                " ": "%20",
                "!": "%21", 
                "#": "%23",
                "$": "%24",
                "&": "%26",
                "'": "%27",
                "(": "%28",
                ")": "%29",
                "*": "%2A",
                "+": "%2B",
                ",": "%2C",
                "/": "%2F",
                ":": "%3A",
                ";": "%3B",
                "=": "%3D",
                "?": "%3F",
                "@": "%40",
                "[": "%5B",
                "]": "%5D"
            }
        },
        "safe_contexts": {
            "path": "Forward slashes (/) often kept safe",
            "query": "= and & often kept safe for parameters",
            "fragment": "Usually encode everything",
            "form_data": "Often use + for spaces"
        }
    })


@url_encoder_router.get(
    "/info",
    summary="Get URL encoder information", 
    description="Get information about URL encoding"
)
async def get_url_encoder_info(
    service: URLEncoderService = Depends(get_url_encoder_service)
) -> JSONResponse:
    """
    Get URL encoder information.
    
    Returns information about URL encoding capabilities.
    """
    return JSONResponse(content={
        "encoder": "URL Encoding",
        "description": "Encode text for safe transmission in URLs using percent-encoding",
        "standards": [
            "RFC 3986 (URI Generic Syntax)",
            "HTML form data encoding",
            "application/x-www-form-urlencoded"
        ],
        "encoding_types": {
            "quote": "Standard URL encoding with %XX format",
            "quote_plus": "Form encoding with + for spaces"
        },
        "use_cases": [
            "URL path components",
            "Query parameters",
            "Form data submission",
            "API endpoint paths",
            "Search query encoding"
        ],
        "parameters": {
            "safe": {
                "type": "string",
                "default": "",
                "description": "Characters to not encode"
            },
            "encoding": {
                "type": "string", 
                "default": "utf-8",
                "description": "Character encoding"
            },
            "plus_encoding": {
                "type": "boolean",
                "default": False,
                "description": "Use + for spaces"
            }
        }
    })