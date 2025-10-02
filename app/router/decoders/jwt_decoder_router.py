"""
JWT decoder router.
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional, Dict, Any
import json

from app.services.decoders.jwt_decoder import JWTDecoderService, get_jwt_decoder_service

jwt_decoder_router = APIRouter(prefix="/decode/jwt", tags=["JWT Decoder"])


@jwt_decoder_router.post(
    "/token",
    summary="Decode JWT token",
    description="Decode and verify JWT token"
)
async def decode_jwt_token(
    token: str = Form(..., description="JWT token to decode"),
    secret: str = Form(default="your-secret-key", description="Secret key for verification"),
    algorithm: str = Query(default="HS256", description="Expected signing algorithm"),
    verify: bool = Query(default=True, description="Verify token signature"),
    verify_exp: bool = Query(default=True, description="Verify expiration"),
    audience: Optional[str] = Query(default=None, description="Expected audience"),
    issuer: Optional[str] = Query(default=None, description="Expected issuer"),
    raw_output: bool = Query(default=False, description="Return raw binary data if payload contains base64"),
    service: JWTDecoderService = Depends(get_jwt_decoder_service)
) -> JSONResponse:
    """
    Decode JWT token.
    
    - **token**: JWT token to decode
    - **secret**: Secret key for verification
    - **algorithm**: Expected signing algorithm
    - **verify**: Whether to verify token signature
    - **verify_exp**: Whether to verify expiration
    - **audience**: Expected audience claim
    - **issuer**: Expected issuer claim
    - **raw_output**: Return raw binary data for base64 payload
    
    Returns decoded JWT payload.
    """
    try:
        options = {}
        if not verify_exp:
            options['verify_exp'] = False
        
        payload = await service.decode(
            token,
            secret=secret,
            algorithm=algorithm,
            verify=verify,
            verify_exp=verify_exp,
            audience=audience,
            issuer=issuer,
            options=options,
            raw_output=raw_output
        )
        
        # If raw_output and we get bytes, return as downloadable file
        if raw_output and isinstance(payload, bytes):
            return StreamingResponse(
                iter([payload]),
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": "attachment; filename=jwt_decoded_data.bin"
                }
            )
        
        return JSONResponse(content={
            "payload": payload,
            "verified": verify,
            "algorithm": algorithm,
            "audience_verified": audience,
            "issuer_verified": issuer
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JWT decoding failed: {str(e)}")


@jwt_decoder_router.post(
    "/file",
    summary="Decode JWT from file",
    description="Decode JWT token from uploaded file"
)
async def decode_jwt_file(
    file: UploadFile = File(...),
    secret: str = Form(default="your-secret-key", description="Secret key for verification"),
    algorithm: str = Query(default="HS256", description="Expected signing algorithm"),
    verify: bool = Query(default=True, description="Verify token signature"),
    service: JWTDecoderService = Depends(get_jwt_decoder_service)
) -> JSONResponse:
    """
    Decode JWT token from file.
    
    - **file**: File containing JWT token
    - **secret**: Secret key for verification
    - **algorithm**: Expected signing algorithm
    - **verify**: Whether to verify token signature
    
    Returns decoded JWT payload.
    """
    try:
        payload = await service.decode_file(
            file,
            secret=secret,
            algorithm=algorithm,
            verify=verify
        )
        
        return JSONResponse(content={
            "payload": payload,
            "verified": verify,
            "algorithm": algorithm,
            "source_file": file.filename
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JWT decoding failed: {str(e)}")


@jwt_decoder_router.post(
    "/inspect",
    summary="Inspect JWT token without verification",
    description="Get JWT token information without signature verification"
)
async def inspect_jwt_token(
    token: str = Form(..., description="JWT token to inspect"),
    service: JWTDecoderService = Depends(get_jwt_decoder_service)
) -> JSONResponse:
    """
    Inspect JWT token structure without verification.
    
    - **token**: JWT token to inspect
    
    Returns token information and structure.
    """
    try:
        # Get basic token info
        token_info = service.get_token_info(token)
        
        # Try to decode payload without verification
        payload = await service.decode(token, verify=False)
        
        return JSONResponse(content={
            "token_info": token_info,
            "payload": payload,
            "verified": False,
            "warning": "Token signature was not verified"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JWT inspection failed: {str(e)}")


@jwt_decoder_router.post(
    "/header",
    summary="Decode JWT header",
    description="Decode only the JWT header without verification"
)
async def decode_jwt_header(
    token: str = Form(..., description="JWT token"),
    service: JWTDecoderService = Depends(get_jwt_decoder_service)
) -> JSONResponse:
    """
    Decode JWT header only.
    
    - **token**: JWT token
    
    Returns JWT header information.
    """
    try:
        header = service.decode_header(token)
        
        return JSONResponse(content={
            "header": header,
            "algorithm": header.get("alg"),
            "type": header.get("typ", "JWT"),
            "key_id": header.get("kid"),
            "content_type": header.get("cty")
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JWT header decoding failed: {str(e)}")


@jwt_decoder_router.post(
    "/validate",
    summary="Validate JWT token format",
    description="Validate JWT token format without decoding"
)
async def validate_jwt_format(
    token: str = Form(..., description="JWT token to validate"),
    service: JWTDecoderService = Depends(get_jwt_decoder_service)
) -> JSONResponse:
    """
    Validate JWT token format.
    
    - **token**: JWT token to validate
    
    Returns validation results.
    """
    try:
        is_valid = service.validate_token_format(token)
        parts = token.split('.')
        
        result = {
            "valid_format": is_valid,
            "parts_count": len(parts),
            "expected_parts": 3,
            "token_length": len(token)
        }
        
        if is_valid:
            try:
                header = service.decode_header(token)
                result["header_valid"] = True
                result["algorithm"] = header.get("alg")
                result["type"] = header.get("typ")
            except:
                result["header_valid"] = False
        else:
            result["header_valid"] = False
        
        return JSONResponse(content=result)
        
    except Exception as e:
        return JSONResponse(content={
            "valid_format": False,
            "error": str(e)
        })


@jwt_decoder_router.get(
    "/info",
    summary="Get JWT decoder information",
    description="Get information about JWT decoding"
)
async def get_jwt_decoder_info(
    service: JWTDecoderService = Depends(get_jwt_decoder_service)
) -> JSONResponse:
    """
    Get JWT decoder information.
    
    Returns information about JWT decoding capabilities.
    """
    return JSONResponse(content={
        "decoder": "JWT (JSON Web Token)",
        "description": "Decode and verify JWT tokens for secure data retrieval",
        "operations": {
            "decode": "Full token decoding with signature verification",
            "inspect": "View token contents without verification",
            "header": "Decode only the token header",
            "validate": "Check token format validity"
        },
        "verification_options": {
            "signature": "Verify token signature with secret key",
            "expiration": "Check if token has expired",
            "audience": "Verify expected audience claim",
            "issuer": "Verify expected issuer claim"
        },
        "security_features": [
            "Signature verification",
            "Expiration checking", 
            "Audience validation",
            "Issuer validation",
            "Algorithm verification"
        ],
        "common_errors": {
            "expired": "Token has expired (exp claim)",
            "invalid_signature": "Signature verification failed",
            "invalid_format": "Token format is not valid JWT",
            "algorithm_mismatch": "Algorithm doesn't match expected"
        },
        "best_practices": [
            "Always verify signatures in production",
            "Check expiration times",
            "Validate audience and issuer claims",
            "Use strong secret keys",
            "Handle errors gracefully"
        ]
    })