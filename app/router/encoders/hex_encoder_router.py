"""
Hex encoder router.
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional

from app.services.encoders.hex_encoder import HexEncoderService, get_hex_encoder_service

hex_encoder_router = APIRouter(prefix="/encode/hex", tags=["Hex Encoder"])


@hex_encoder_router.post(
    "/text",
    summary="Encode text to hexadecimal",
    description="Convert text string to hexadecimal representation"
)
async def encode_text_to_hex(
    text: str = Form(..., description="Text to encode to hex"),
    uppercase: bool = Query(default=False, description="Use uppercase hex digits"),
    separator: str = Query(default="", description="Separator between hex bytes"),
    prefix: str = Query(default="", description="Prefix for hex output"),
    encoding: str = Query(default="utf-8", description="Text encoding"),
    service: HexEncoderService = Depends(get_hex_encoder_service)
) -> JSONResponse:
    """
    Encode text to hexadecimal.
    
    - **text**: Text to be hex encoded
    - **uppercase**: Use uppercase hex digits (A-F vs a-f)
    - **separator**: Separator between hex bytes (e.g., ":", " ", "-")
    - **prefix**: Prefix for hex output (e.g., "0x", "\\x")
    - **encoding**: Text encoding to use
    
    Returns hexadecimal encoded text.
    """
    try:
        # Convert text to bytes with specified encoding
        byte_data = text.encode(encoding)
        
        encoded_hex = await service.encode(
            byte_data,
            uppercase=uppercase,
            separator=separator,
            prefix=prefix
        )
        
        return JSONResponse(content={
            "input": text,
            "encoded": encoded_hex,
            "encoding": encoding,
            "byte_count": len(byte_data),
            "hex_length": len(encoded_hex),
            "options": {
                "uppercase": uppercase,
                "separator": separator,
                "prefix": prefix
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hex encoding failed: {str(e)}")


@hex_encoder_router.post(
    "/file",
    summary="Encode file to hexadecimal", 
    description="Convert file content to hexadecimal representation"
)
async def encode_file_to_hex(
    file: UploadFile = File(...),
    uppercase: bool = Query(default=False, description="Use uppercase hex digits"),
    separator: str = Query(default="", description="Separator between hex bytes"),
    prefix: str = Query(default="", description="Prefix for hex output"),
    return_stream: bool = Query(default=False, description="Return as streaming response"),
    service: HexEncoderService = Depends(get_hex_encoder_service)
) -> StreamingResponse:
    """
    Encode file content to hexadecimal.
    
    - **file**: File to be hex encoded
    - **uppercase**: Use uppercase hex digits
    - **separator**: Separator between hex bytes
    - **prefix**: Prefix for hex output
    - **return_stream**: Return as streaming response
    
    Returns hexadecimal encoded file content.
    """
    try:
        if return_stream:
            # Return as streaming response
            hex_stream = service.encode_stream(
                file,
                uppercase=uppercase,
                separator=separator,
                prefix=prefix
            )
            output_filename = service.get_output_filename(file.filename or "unknown")
            
            return StreamingResponse(
                hex_stream,
                media_type="text/plain",
                headers={
                    "Content-Disposition": f"attachment; filename={output_filename}"
                }
            )
        else:
            # Return as direct response
            encoded_hex = await service.encode_file(
                file,
                uppercase=uppercase,
                separator=separator,
                prefix=prefix
            )
            output_filename = service.get_output_filename(file.filename or "unknown")
            
            return StreamingResponse(
                iter([encoded_hex.encode('utf-8')]),
                media_type="text/plain",
                headers={
                    "Content-Disposition": f"attachment; filename={output_filename}"
                }
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hex encoding failed: {str(e)}")


@hex_encoder_router.post(
    "/ascii",
    summary="Encode ASCII text to hex",
    description="Convert ASCII text to hex representation"
)
async def encode_ascii_to_hex(
    ascii_text: str = Form(..., description="ASCII text to encode"),
    uppercase: bool = Query(default=False, description="Use uppercase hex digits"),
    separator: str = Query(default=" ", description="Separator between hex bytes"),
    prefix: str = Query(default="", description="Prefix for hex output"),
    service: HexEncoderService = Depends(get_hex_encoder_service)
) -> JSONResponse:
    """
    Encode ASCII text to hexadecimal.
    
    - **ascii_text**: ASCII text to encode
    - **uppercase**: Use uppercase hex digits
    - **separator**: Separator between hex bytes
    - **prefix**: Prefix for hex output
    
    Returns hex encoded ASCII text.
    """
    try:
        # Validate ASCII
        try:
            ascii_text.encode('ascii')
        except UnicodeEncodeError:
            raise HTTPException(status_code=400, detail="Text contains non-ASCII characters")
        
        encoded_hex = await service.encode_ascii_hex(
            ascii_text,
            uppercase=uppercase,
            separator=separator,
            prefix=prefix
        )
        
        # Create character mapping for display
        char_mapping = []
        for char in ascii_text:
            hex_val = f"{ord(char):02x}"
            if uppercase:
                hex_val = hex_val.upper()
            if prefix:
                hex_val = prefix + hex_val
            char_mapping.append({
                "char": char,
                "ascii_code": ord(char),
                "hex": hex_val
            })
        
        return JSONResponse(content={
            "input": ascii_text,
            "encoded": encoded_hex,
            "char_mapping": char_mapping,
            "options": {
                "uppercase": uppercase,
                "separator": separator,
                "prefix": prefix
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ASCII hex encoding failed: {str(e)}")


@hex_encoder_router.post(
    "/with_length",
    summary="Encode with length prefix",
    description="Encode data with length prefix in hex"
)
async def encode_with_length_prefix(
    data: str = Form(..., description="Data to encode with length prefix"),
    encoding: str = Query(default="utf-8", description="Text encoding"),
    uppercase: bool = Query(default=False, description="Use uppercase hex digits"),
    service: HexEncoderService = Depends(get_hex_encoder_service)
) -> JSONResponse:
    """
    Encode data with length prefix.
    
    - **data**: Data to encode
    - **encoding**: Text encoding to use
    - **uppercase**: Use uppercase hex digits
    
    Returns length-prefixed hex encoded data.
    """
    try:
        encoded_hex = await service.encode_with_length(
            data,
            encoding=encoding,
            uppercase=uppercase
        )
        
        # Calculate components for display
        byte_data = data.encode(encoding)
        data_length = len(byte_data)
        length_hex = f"{data_length:04x}"
        if uppercase:
            length_hex = length_hex.upper()
        
        return JSONResponse(content={
            "input": data,
            "encoded": encoded_hex,
            "encoding": encoding,
            "data_length": data_length,
            "length_hex": length_hex,
            "data_hex": encoded_hex[4:],  # Remove length prefix
            "format": "LLLLDDDD... (L=length, D=data)"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Length-prefixed encoding failed: {str(e)}")


@hex_encoder_router.get(
    "/formats",
    summary="Get hex format examples",
    description="Get examples of different hex encoding formats"
)
async def get_hex_formats() -> JSONResponse:
    """
    Get hex format examples.
    
    Returns examples of different hexadecimal encoding formats.
    """
    sample_text = "Hello"
    sample_bytes = sample_text.encode('utf-8')
    
    formats = {
        "basic_lowercase": sample_bytes.hex(),
        "basic_uppercase": sample_bytes.hex().upper(),
        "space_separated": " ".join([f"{b:02x}" for b in sample_bytes]),
        "colon_separated": ":".join([f"{b:02x}" for b in sample_bytes]),
        "dash_separated": "-".join([f"{b:02x}" for b in sample_bytes]),
        "0x_prefixed": " ".join([f"0x{b:02x}" for b in sample_bytes]),
        "backslash_x": "".join([f"\\x{b:02x}" for b in sample_bytes]),
        "c_array": "{" + ", ".join([f"0x{b:02x}" for b in sample_bytes]) + "}"
    }
    
    return JSONResponse(content={
        "sample_input": sample_text,
        "sample_bytes": list(sample_bytes),
        "formats": formats,
        "use_cases": {
            "basic": "Simple hex dump, debugging",
            "space_separated": "Readable hex output", 
            "colon_separated": "MAC addresses, some protocols",
            "dash_separated": "UUIDs, some identifiers",
            "0x_prefixed": "Programming contexts",
            "backslash_x": "String literals, escape sequences",
            "c_array": "C/C++ byte arrays"
        }
    })


@hex_encoder_router.get(
    "/info",
    summary="Get hex encoder information",
    description="Get information about hexadecimal encoding"
)
async def get_hex_encoder_info(
    service: HexEncoderService = Depends(get_hex_encoder_service)
) -> JSONResponse:
    """
    Get hex encoder information.
    
    Returns information about hexadecimal encoding capabilities.
    """
    return JSONResponse(content={
        "encoder": "Hexadecimal Encoding",
        "description": "Convert binary data to hexadecimal representation",
        "hex_digits": "0123456789abcdef (or ABCDEF for uppercase)",
        "encoding_format": "Each byte becomes 2 hex characters",
        "features": [
            "Uppercase/lowercase hex digits",
            "Custom separators between bytes",
            "Custom prefixes for hex values", 
            "Length-prefixed encoding",
            "ASCII text encoding"
        ],
        "common_separators": {
            "none": "48656c6c6f",
            "space": "48 65 6c 6c 6f",
            "colon": "48:65:6c:6c:6f", 
            "dash": "48-65-6c-6c-6f"
        },
        "common_prefixes": {
            "0x": "0x48 0x65 0x6c 0x6c 0x6f",
            "\\x": "\\x48\\x65\\x6c\\x6c\\x6f",
            "#": "#48 #65 #6c #6c #6f"
        },
        "use_cases": [
            "Binary file analysis",
            "Debugging binary data",
            "Protocol analysis",
            "Cryptographic key display",
            "Memory dumps",
            "Checksum calculation"
        ]
    })