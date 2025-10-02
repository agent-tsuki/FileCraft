"""
URL decoder router.
"""

from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional, Dict, Any

from app.services.decoders.url_decoder import URLDecoderService, get_url_decoder_service

url_decoder_router = APIRouter(prefix="/decode/url", tags=["URL Decoder"])


@url_decoder_router.post(
    "/text",
    summary="Decode URL encoded text",
    description="Decode URL encoded text string",
)
async def decode_url_text(
    encoded_text: str = Form(..., description="URL encoded text to decode"),
    encoding: str = Query(default="utf-8", description="Character encoding"),
    errors: str = Query(
        default="replace",
        enum=["strict", "ignore", "replace"],
        description="Error handling",
    ),
    plus_spaces: bool = Query(default=False, description="Treat + as spaces"),
    service: URLDecoderService = Depends(get_url_decoder_service),
) -> JSONResponse:
    """
    Decode URL encoded text.

    - **encoded_text**: URL encoded text to decode
    - **encoding**: Character encoding to use
    - **errors**: Error handling method
    - **plus_spaces**: Treat + characters as spaces

    Returns decoded text.
    """
    try:
        if plus_spaces:
            decoded_text = service.decode_plus(
                encoded_text, encoding=encoding, errors=errors
            )
        else:
            decoded_text = await service.decode(
                encoded_text, encoding=encoding, errors=errors
            )

        return JSONResponse(
            content={
                "input": encoded_text,
                "decoded": decoded_text,
                "encoding": encoding,
                "errors": errors,
                "plus_spaces": plus_spaces,
                "length_original": len(encoded_text),
                "length_decoded": len(decoded_text),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL decoding failed: {str(e)}")


@url_decoder_router.post(
    "/file",
    summary="Decode URL encoded file",
    description="Decode URL encoded file content",
)
async def decode_url_file(
    file: UploadFile = File(...),
    encoding: str = Query(default="utf-8", description="Character encoding"),
    errors: str = Query(
        default="replace",
        enum=["strict", "ignore", "replace"],
        description="Error handling",
    ),
    service: URLDecoderService = Depends(get_url_decoder_service),
) -> StreamingResponse:
    """
    Decode URL encoded file content.

    - **file**: File containing URL encoded data
    - **encoding**: Character encoding to use
    - **errors**: Error handling method

    Returns decoded file content.
    """
    try:
        decoded_content = await service.decode_file(
            file, encoding=encoding, errors=errors
        )
        output_filename = service.get_output_filename(file.filename or "unknown")

        return StreamingResponse(
            iter([decoded_content.encode("utf-8")]),
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL decoding failed: {str(e)}")


@url_decoder_router.post(
    "/params",
    summary="Decode URL query parameters",
    description="Parse and decode URL query parameter string",
)
async def decode_url_params(
    query_string: str = Form(..., description="URL query string to parse"),
    keep_blank_values: bool = Query(
        default=False, description="Keep blank parameter values"
    ),
    strict_parsing: bool = Query(default=False, description="Use strict parsing"),
    encoding: str = Query(default="utf-8", description="Character encoding"),
    max_num_fields: Optional[int] = Query(
        default=None, description="Maximum number of fields"
    ),
    service: URLDecoderService = Depends(get_url_decoder_service),
) -> JSONResponse:
    """
    Parse and decode URL query parameters.

    - **query_string**: Query string to parse (without leading ?)
    - **keep_blank_values**: Keep parameters with blank values
    - **strict_parsing**: Use strict parsing (raise errors on bad data)
    - **encoding**: Character encoding to use
    - **max_num_fields**: Maximum number of fields to parse

    Returns parsed and decoded parameters.
    """
    try:
        # Remove leading ? if present
        if query_string.startswith("?"):
            query_string = query_string[1:]

        params = service.decode_query_params(
            query_string,
            keep_blank_values=keep_blank_values,
            strict_parsing=strict_parsing,
            encoding=encoding,
            max_num_fields=max_num_fields,
        )

        return JSONResponse(
            content={
                "input_query": query_string,
                "parsed_params": params,
                "param_count": len(params),
                "encoding": encoding,
                "options": {
                    "keep_blank_values": keep_blank_values,
                    "strict_parsing": strict_parsing,
                    "max_num_fields": max_num_fields,
                },
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Parameter parsing failed: {str(e)}"
        )


@url_decoder_router.post(
    "/parse",
    summary="Parse complete URL",
    description="Parse complete URL into components",
)
async def parse_complete_url(
    url: str = Form(..., description="Complete URL to parse"),
    service: URLDecoderService = Depends(get_url_decoder_service),
) -> JSONResponse:
    """
    Parse complete URL into its components.

    - **url**: Complete URL to parse

    Returns URL components.
    """
    try:
        parsed_url = service.parse_url(url)

        # Decode query parameters if present
        decoded_params = {}
        if parsed_url.get("query"):
            try:
                decoded_params = service.decode_query_params(parsed_url["query"])
            except:
                decoded_params = {"error": "Failed to parse query parameters"}

        return JSONResponse(
            content={
                "input_url": url,
                "components": parsed_url,
                "decoded_query_params": decoded_params,
                "reconstructed_url": f"{parsed_url.get('scheme', '')}://{parsed_url.get('netloc', '')}{parsed_url.get('path', '')}",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL parsing failed: {str(e)}")


@url_decoder_router.post(
    "/analyze",
    summary="Analyze URL encoded content",
    description="Analyze URL encoded content without full decoding",
)
async def analyze_url_content(
    encoded_text: str = Form(..., description="URL encoded text to analyze"),
    service: URLDecoderService = Depends(get_url_decoder_service),
) -> JSONResponse:
    """
    Analyze URL encoded content.

    - **encoded_text**: URL encoded text to analyze

    Returns analysis of the encoded content.
    """
    try:
        import re

        # Count percent-encoded characters
        percent_encoded = re.findall(r"%[0-9A-Fa-f]{2}", encoded_text)
        plus_count = encoded_text.count("+")

        # Try to identify common patterns
        has_query_params = "=" in encoded_text and "&" in encoded_text
        has_path_separators = "/" in encoded_text

        analysis = {
            "input_length": len(encoded_text),
            "percent_encoded_chars": len(percent_encoded),
            "plus_characters": plus_count,
            "percent_encoded_list": percent_encoded[:20],  # Show first 20
            "likely_type": "unknown",
        }

        # Guess content type
        if has_query_params:
            analysis["likely_type"] = "query_parameters"
        elif has_path_separators:
            analysis["likely_type"] = "url_path"
        elif plus_count > 0:
            analysis["likely_type"] = "form_data"
        elif len(percent_encoded) > 0:
            analysis["likely_type"] = "url_encoded_text"

        # Try to safely decode for preview
        try:
            preview = await service.decode(encoded_text[:100])
            analysis["preview"] = preview[:100]
        except:
            analysis["preview"] = "Unable to decode for preview"

        return JSONResponse(content=analysis)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@url_decoder_router.get(
    "/info",
    summary="Get URL decoder information",
    description="Get information about URL decoding",
)
async def get_url_decoder_info(
    service: URLDecoderService = Depends(get_url_decoder_service),
) -> JSONResponse:
    """
    Get URL decoder information.

    Returns information about URL decoding capabilities.
    """
    return JSONResponse(
        content={
            "decoder": "URL Decoding",
            "description": "Decode percent-encoded URLs and parse URL components",
            "decoding_types": {
                "unquote": "Standard URL decoding from %XX format",
                "unquote_plus": "Form decoding with + as spaces",
                "parse_qs": "Query string parameter parsing",
            },
            "capabilities": [
                "Percent-encoded character decoding",
                "Query parameter parsing",
                "Complete URL parsing",
                "Form data decoding",
                "Error handling options",
            ],
            "common_encodings": {
                "%20": "space",
                "%21": "!",
                "%22": '"',
                "%23": "#",
                "%24": "$",
                "%25": "%",
                "%26": "&",
                "%2B": "+",
                "%2F": "/",
                "%3D": "=",
                "%3F": "?",
            },
            "parameters": {
                "encoding": {
                    "type": "string",
                    "default": "utf-8",
                    "description": "Character encoding for decoding",
                },
                "errors": {
                    "type": "string",
                    "default": "replace",
                    "options": ["strict", "ignore", "replace"],
                    "description": "Error handling method",
                },
                "plus_spaces": {
                    "type": "boolean",
                    "default": False,
                    "description": "Treat + as spaces (form encoding)",
                },
            },
            "use_cases": [
                "Decoding URL paths",
                "Processing query parameters",
                "Form data processing",
                "API parameter extraction",
                "URL analysis and debugging",
            ],
        }
    )
