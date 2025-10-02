"""
Main encoder/decoder router combining all encoding/decoding functionality.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from .encoders import (
    base64_encoder_router,
    jwt_encoder_router,
    url_encoder_router,
    hex_encoder_router,
    hash_encoder_router,
)
from .decoders import (
    base64_decoder_router,
    jwt_decoder_router,
    url_decoder_router,
    hex_decoder_router,
)

# Create main router
encoder_decoder_router = APIRouter(prefix="/codec", tags=["Encoder/Decoder"])

# Include all encoder routers
encoder_decoder_router.include_router(base64_encoder_router)
encoder_decoder_router.include_router(jwt_encoder_router)
encoder_decoder_router.include_router(url_encoder_router)
encoder_decoder_router.include_router(hex_encoder_router)
encoder_decoder_router.include_router(hash_encoder_router)

# Include all decoder routers
encoder_decoder_router.include_router(base64_decoder_router)
encoder_decoder_router.include_router(jwt_decoder_router)
encoder_decoder_router.include_router(url_decoder_router)
encoder_decoder_router.include_router(hex_decoder_router)


@encoder_decoder_router.get(
    "/",
    summary="Encoder/Decoder Overview",
    description="Get overview of all available encoding and decoding capabilities",
)
async def get_encoder_decoder_overview() -> JSONResponse:
    """
    Get complete overview of encoder/decoder system.

    Returns information about all available encoders and decoders.
    """
    return JSONResponse(
        content={
            "system": "FileCraft Encoder/Decoder System",
            "version": "1.0.0",
            "description": "Comprehensive encoding and decoding service for various formats",
            "encoders": {
                "base64": {
                    "description": "Base64 encoding for binary data",
                    "endpoint": "/codec/encode/base64",
                    "formats": ["standard", "url_safe"],
                    "use_cases": [
                        "File transmission",
                        "Data serialization",
                        "Email attachments",
                    ],
                },
                "jwt": {
                    "description": "JSON Web Token creation and signing",
                    "endpoint": "/codec/encode/jwt",
                    "algorithms": ["HS256", "HS384", "HS512", "RS256", "ES256"],
                    "use_cases": [
                        "Authentication",
                        "API authorization",
                        "Secure data exchange",
                    ],
                },
                "url": {
                    "description": "URL encoding for web safety",
                    "endpoint": "/codec/encode/url",
                    "formats": ["percent_encoding", "form_encoding"],
                    "use_cases": ["URL parameters", "Form data", "Path components"],
                },
                "hex": {
                    "description": "Hexadecimal representation of binary data",
                    "endpoint": "/codec/encode/hex",
                    "formats": ["plain", "separated", "prefixed"],
                    "use_cases": ["Binary analysis", "Debugging", "Protocol analysis"],
                },
                "hash": {
                    "description": "Cryptographic hash generation",
                    "endpoint": "/codec/encode/hash",
                    "algorithms": ["MD5", "SHA1", "SHA256", "SHA512", "SHA3", "BLAKE2"],
                    "use_cases": [
                        "Data integrity",
                        "Password storage",
                        "Digital signatures",
                    ],
                },
            },
            "decoders": {
                "base64": {
                    "description": "Base64 decoding back to binary data",
                    "endpoint": "/codec/decode/base64",
                    "features": [
                        "Auto-detection",
                        "Padding correction",
                        "Format validation",
                    ],
                },
                "jwt": {
                    "description": "JWT token verification and payload extraction",
                    "endpoint": "/codec/decode/jwt",
                    "features": [
                        "Signature verification",
                        "Expiration checking",
                        "Header inspection",
                    ],
                },
                "url": {
                    "description": "URL decoding from percent-encoded format",
                    "endpoint": "/codec/decode/url",
                    "features": [
                        "Parameter parsing",
                        "Component extraction",
                        "Error handling",
                    ],
                },
                "hex": {
                    "description": "Hexadecimal to binary conversion",
                    "endpoint": "/codec/decode/hex",
                    "features": ["Format cleaning", "Separator removal", "Validation"],
                },
            },
            "features": {
                "streaming": "Support for large files via streaming responses",
                "validation": "Input validation and error handling",
                "multiple_formats": "Various output formats for flexibility",
                "security": "Secure handling of sensitive data",
                "performance": "Optimized for speed and memory efficiency",
            },
            "api_patterns": {
                "encoders": {
                    "text": "POST /encode/{type}/text - Encode text input",
                    "file": "POST /encode/{type}/file - Encode file content",
                    "info": "GET /encode/{type}/info - Get encoder information",
                },
                "decoders": {
                    "text": "POST /decode/{type}/text - Decode text input",
                    "file": "POST /decode/{type}/file - Decode file content",
                    "validate": "POST /decode/{type}/validate - Validate format",
                    "info": "GET /decode/{type}/info - Get decoder information",
                },
            },
            "supported_types": ["base64", "jwt", "url", "hex", "hash"],
            "getting_started": {
                "encode_text": "Use POST /codec/encode/{type}/text with form data",
                "encode_file": "Use POST /codec/encode/{type}/file with file upload",
                "decode_text": "Use POST /codec/decode/{type}/text with encoded data",
                "get_info": "Use GET /codec/encode/{type}/info for documentation",
            },
        }
    )


@encoder_decoder_router.get(
    "/formats",
    summary="Supported Formats",
    description="Get list of all supported encoding/decoding formats",
)
async def get_supported_formats() -> JSONResponse:
    """
    Get list of all supported formats.

    Returns comprehensive list of supported encoding and decoding formats.
    """
    return JSONResponse(
        content={
            "encoding_formats": {
                "base64": {
                    "name": "Base64",
                    "description": "Binary-to-text encoding",
                    "mime_types": ["text/plain"],
                    "extensions": [".b64", ".base64"],
                    "reversible": True,
                },
                "jwt": {
                    "name": "JSON Web Token",
                    "description": "Signed JSON tokens",
                    "mime_types": ["application/jwt"],
                    "extensions": [".jwt"],
                    "reversible": True,
                },
                "url": {
                    "name": "URL Encoding",
                    "description": "Percent-encoding for URLs",
                    "mime_types": ["text/plain"],
                    "extensions": [".url"],
                    "reversible": True,
                },
                "hex": {
                    "name": "Hexadecimal",
                    "description": "Binary data as hex digits",
                    "mime_types": ["text/plain"],
                    "extensions": [".hex"],
                    "reversible": True,
                },
                "hash": {
                    "name": "Cryptographic Hash",
                    "description": "One-way hash functions",
                    "mime_types": ["text/plain"],
                    "extensions": [".md5", ".sha1", ".sha256", ".sha512"],
                    "reversible": False,
                },
            },
            "input_types": [
                "text/plain",
                "application/octet-stream",
                "application/json",
                "multipart/form-data",
            ],
            "output_types": [
                "text/plain",
                "application/json",
                "application/octet-stream",
                "application/jwt",
            ],
            "notes": {
                "reversible": "Formats marked as reversible can be decoded back to original data",
                "hashing": "Hash functions are one-way and cannot be reversed",
                "streaming": "All formats support streaming for large files",
                "validation": "All decoders include format validation",
            },
        }
    )


# Export the main router
__all__ = ["encoder_decoder_router"]
