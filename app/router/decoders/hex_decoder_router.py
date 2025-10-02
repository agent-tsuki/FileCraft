"""
Hex decoder router.
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional

from app.services.decoders.hex_decoder import HexDecoderService, get_hex_decoder_service

hex_decoder_router = APIRouter(prefix="/decode/hex", tags=["Hex Decoder"])


@hex_decoder_router.post(
    "/text",
    summary="Decode hexadecimal text",
    description="Convert hexadecimal string back to original data"
)
async def decode_hex_text(
    hex_text: str = Form(..., description="Hexadecimal text to decode"),
    ignore_whitespace: bool = Query(default=True, description="Ignore whitespace in hex"),
    ignore_separators: bool = Query(default=True, description="Ignore common separators"),
    strict: bool = Query(default=False, description="Strict hex validation"),
    output_format: str = Query(default="text", enum=["text", "binary", "base64"], description="Output format"),
    encoding: str = Query(default="utf-8", description="Text encoding for text output"),
    service: HexDecoderService = Depends(get_hex_decoder_service)
) -> JSONResponse:
    """
    Decode hexadecimal text.
    
    - **hex_text**: Hexadecimal text to decode
    - **ignore_whitespace**: Ignore whitespace in input
    - **ignore_separators**: Ignore common separators (: - _ space)
    - **strict**: Strict hex validation
    - **output_format**: Output format (text, binary, base64)
    - **encoding**: Text encoding for text output
    
    Returns decoded data in requested format.
    """
    try:
        decoded_bytes = await service.decode(
            hex_text,
            ignore_whitespace=ignore_whitespace,
            ignore_separators=ignore_separators,
            strict=strict
        )
        
        result = {
            "input": hex_text[:200] + "..." if len(hex_text) > 200 else hex_text,
            "input_length": len(hex_text),
            "decoded_size": len(decoded_bytes),
            "format": output_format
        }
        
        if output_format == "text":
            try:
                result["decoded"] = decoded_bytes.decode(encoding)
                result["encoding"] = encoding
            except UnicodeDecodeError:
                result["decoded"] = "<Binary data cannot be displayed as text>"
                result["encoding"] = f"{encoding} (failed)"
                result["error"] = "Binary data contains non-text bytes"
        elif output_format == "binary":
            result["decoded"] = list(decoded_bytes)
        elif output_format == "base64":
            import base64
            result["decoded"] = base64.b64encode(decoded_bytes).decode('ascii')
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hex decoding failed: {str(e)}")


@hex_decoder_router.post(
    "/file",
    summary="Decode hexadecimal file",
    description="Decode file containing hexadecimal data"
)
async def decode_hex_file(
    file: UploadFile = File(...),
    ignore_whitespace: bool = Query(default=True, description="Ignore whitespace in hex"),
    ignore_separators: bool = Query(default=True, description="Ignore common separators"),
    strict: bool = Query(default=False, description="Strict hex validation"),
    service: HexDecoderService = Depends(get_hex_decoder_service)
) -> StreamingResponse:
    """
    Decode hexadecimal file content.
    
    - **file**: File containing hexadecimal data
    - **ignore_whitespace**: Ignore whitespace in input
    - **ignore_separators**: Ignore common separators
    - **strict**: Strict hex validation
    
    Returns decoded binary content.
    """
    try:
        decoded_bytes = await service.decode_file(
            file,
            ignore_whitespace=ignore_whitespace,
            ignore_separators=ignore_separators,
            strict=strict
        )
        
        output_filename = service.get_output_filename(file.filename or "unknown")
        
        return StreamingResponse(
            iter([decoded_bytes]),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hex decoding failed: {str(e)}")


@hex_decoder_router.post(
    "/to_text",
    summary="Decode hex to text",
    description="Decode hexadecimal directly to text string"
)
async def decode_hex_to_text(
    hex_text: str = Form(..., description="Hexadecimal text to decode to text"),
    encoding: str = Query(default="utf-8", description="Text encoding"),
    ignore_errors: bool = Query(default=True, description="Ignore decoding errors"),
    service: HexDecoderService = Depends(get_hex_decoder_service)
) -> JSONResponse:
    """
    Decode hexadecimal directly to text.
    
    - **hex_text**: Hexadecimal text to decode
    - **encoding**: Text encoding to use
    - **ignore_errors**: Ignore text decoding errors
    
    Returns decoded text string.
    """
    try:
        decoded_text = await service.decode_to_text(
            hex_text,
            encoding=encoding,
            ignore_whitespace=True,
            ignore_separators=True
        )
        
        # Create character analysis
        char_analysis = []
        for i, char in enumerate(decoded_text[:50]):  # Analyze first 50 chars
            char_analysis.append({
                "char": char,
                "ascii_code": ord(char),
                "hex": f"{ord(char):02x}",
                "is_printable": char.isprintable()
            })
        
        return JSONResponse(content={
            "input": hex_text[:200] + "..." if len(hex_text) > 200 else hex_text,
            "decoded": decoded_text,
            "encoding": encoding,
            "length": len(decoded_text),
            "char_analysis": char_analysis,
            "has_non_printable": any(not c.isprintable() for c in decoded_text)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hex to text decoding failed: {str(e)}")


@hex_decoder_router.post(
    "/with_length",
    summary="Decode length-prefixed hex",
    description="Decode hex data with length prefix"
)
async def decode_hex_with_length(
    hex_data: str = Form(..., description="Length-prefixed hex data"),
    output_format: str = Query(default="text", enum=["text", "binary", "base64"], description="Output format"),
    encoding: str = Query(default="utf-8", description="Text encoding for text output"),
    service: HexDecoderService = Depends(get_hex_decoder_service)
) -> JSONResponse:
    """
    Decode length-prefixed hexadecimal data.
    
    - **hex_data**: Length-prefixed hex string (LLLLDDDD format)
    - **output_format**: Output format (text, binary, base64)
    - **encoding**: Text encoding for text output
    
    Returns decoded data from length-prefixed hex.
    """
    try:
        decoded_bytes = service.decode_with_length_prefix(hex_data)
        
        # Extract length info for display
        cleaned_hex = service._clean_hex_string(hex_data, ignore_whitespace=True, ignore_separators=True)
        length_hex = cleaned_hex[:4]
        data_hex = cleaned_hex[4:]
        expected_length = int(length_hex, 16)
        
        result = {
            "input": hex_data[:200] + "..." if len(hex_data) > 200 else hex_data,
            "length_prefix": length_hex,
            "expected_length": expected_length,
            "actual_length": len(decoded_bytes),
            "data_hex": data_hex[:100] + "..." if len(data_hex) > 100 else data_hex,
            "format": output_format
        }
        
        if output_format == "text":
            try:
                result["decoded"] = decoded_bytes.decode(encoding)
                result["encoding"] = encoding
            except UnicodeDecodeError:
                result["decoded"] = "<Binary data cannot be displayed as text>"
                result["encoding"] = f"{encoding} (failed)"
        elif output_format == "binary":
            result["decoded"] = list(decoded_bytes)
        elif output_format == "base64":
            import base64
            result["decoded"] = base64.b64encode(decoded_bytes).decode('ascii')
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Length-prefixed hex decoding failed: {str(e)}")


@hex_decoder_router.post(
    "/analyze",
    summary="Analyze hex content",
    description="Analyze hexadecimal content without full decoding"
)
async def analyze_hex_content(
    hex_text: str = Form(..., description="Hexadecimal text to analyze"),
    service: HexDecoderService = Depends(get_hex_decoder_service)
) -> JSONResponse:
    """
    Analyze hexadecimal content.
    
    - **hex_text**: Hexadecimal text to analyze
    
    Returns analysis of the hex content.
    """
    try:
        cleaned_hex = service._clean_hex_string(hex_text, ignore_whitespace=True, ignore_separators=True)
        
        analysis = {
            "input_length": len(hex_text),
            "cleaned_length": len(cleaned_hex),
            "byte_count": len(cleaned_hex) // 2,
            "is_valid_hex": service._is_valid_hex(cleaned_hex),
            "is_even_length": len(cleaned_hex) % 2 == 0,
            "has_uppercase": any(c in "ABCDEF" for c in cleaned_hex),
            "has_lowercase": any(c in "abcdef" for c in cleaned_hex),
            "removed_chars": len(hex_text) - len(cleaned_hex)
        }
        
        # Character frequency
        char_freq = {}
        for char in cleaned_hex:
            char_freq[char] = char_freq.get(char, 0) + 1
        analysis["char_frequency"] = char_freq
        
        # Try to decode a sample for preview
        if analysis["is_valid_hex"] and len(cleaned_hex) >= 2:
            try:
                sample_bytes = bytes.fromhex(cleaned_hex[:min(20, len(cleaned_hex))])
                analysis["sample_decoded"] = {
                    "bytes": list(sample_bytes),
                    "ascii_preview": "".join(chr(b) if 32 <= b <= 126 else "." for b in sample_bytes)
                }
            except:
                analysis["sample_decoded"] = "Unable to decode sample"
        
        return JSONResponse(content=analysis)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hex analysis failed: {str(e)}")


@hex_decoder_router.get(
    "/info",
    summary="Get hex decoder information",
    description="Get information about hexadecimal decoding"
)
async def get_hex_decoder_info(
    service: HexDecoderService = Depends(get_hex_decoder_service)
) -> JSONResponse:
    """
    Get hex decoder information.
    
    Returns information about hexadecimal decoding capabilities.
    """
    return JSONResponse(content={
        "decoder": "Hexadecimal Decoding",
        "description": "Convert hexadecimal representation back to binary data",
        "input_formats": [
            "Plain hex: 48656c6c6f",
            "Space separated: 48 65 6c 6c 6f",
            "Colon separated: 48:65:6c:6c:6f",
            "Dash separated: 48-65-6c-6c-6f", 
            "0x prefixed: 0x48 0x65 0x6c 0x6c 0x6f",
            "\\x prefixed: \\x48\\x65\\x6c\\x6c\\x6f"
        ],
        "cleaning_features": [
            "Automatic whitespace removal",
            "Separator removal (: - _ space)",
            "Prefix removal (0x, \\x)",
            "Case insensitive"
        ],
        "output_formats": {
            "text": "Decoded as text string",
            "binary": "Raw binary data as byte array",
            "base64": "Re-encoded as Base64"
        },
        "validation": {
            "character_check": "Only 0-9, A-F, a-f allowed",
            "length_check": "Must be even number of hex characters",
            "strict_mode": "Enforces strict validation"
        },
        "special_features": [
            "Length-prefixed decoding (LLLLDDDD format)",
            "Direct text decoding with encoding support",
            "Content analysis without full decoding",
            "Error handling for malformed input"
        ],
        "use_cases": [
            "Binary file reconstruction",
            "Protocol analysis", 
            "Debugging binary data",
            "Converting hex dumps",
            "Cryptographic data processing"
        ]
    })