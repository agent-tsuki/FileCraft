"""
JWT encoder router.
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional, Dict, Any
import json

from app.services.encoders.jwt_encoder import JWTEncoderService, get_jwt_encoder_service

jwt_encoder_router = APIRouter(prefix="/encode/jwt", tags=["JWT Encoder"])


@jwt_encoder_router.post(
    "/payload",
    summary="Encode JSON payload to JWT",
    description="Create JWT token from JSON payload"
)
async def encode_payload_to_jwt(
    payload: str = Form(..., description="JSON payload to encode"),
    secret: str = Form(default="your-secret-key", description="Secret key for signing"),
    algorithm: str = Query(default="HS256", description="Signing algorithm"),
    exp_minutes: Optional[int] = Query(default=None, description="Expiration time in minutes"),
    issuer: Optional[str] = Query(default=None, description="JWT issuer"),
    audience: Optional[str] = Query(default=None, description="JWT audience"),
    subject: Optional[str] = Query(default=None, description="JWT subject"),
    service: JWTEncoderService = Depends(get_jwt_encoder_service)
) -> JSONResponse:
    """
    Encode JSON payload to JWT token.
    
    - **payload**: JSON payload to encode
    - **secret**: Secret key for signing
    - **algorithm**: Signing algorithm (HS256, HS384, HS512, etc.)
    - **exp_minutes**: Expiration time in minutes
    - **issuer**: JWT issuer claim
    - **audience**: JWT audience claim
    - **subject**: JWT subject claim
    
    Returns JWT token.
    """
    try:
        # Validate JSON payload
        try:
            json.loads(payload)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        token = await service.encode(
            payload,
            secret=secret,
            algorithm=algorithm,
            exp_minutes=exp_minutes,
            issuer=issuer,
            audience=audience,
            subject=subject
        )
        
        return JSONResponse(content={
            "token": token,
            "algorithm": algorithm,
            "expires_in_minutes": exp_minutes,
            "issuer": issuer,
            "audience": audience,
            "subject": subject
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JWT encoding failed: {str(e)}")


@jwt_encoder_router.post(
    "/text",
    summary="Encode text to JWT",
    description="Create JWT token with text data"
)
async def encode_text_to_jwt(
    text: str = Form(..., description="Text to encode"),
    secret: str = Form(default="your-secret-key", description="Secret key for signing"),
    algorithm: str = Query(default="HS256", description="Signing algorithm"),
    exp_minutes: Optional[int] = Query(default=None, description="Expiration time in minutes"),
    service: JWTEncoderService = Depends(get_jwt_encoder_service)
) -> JSONResponse:
    """
    Encode text to JWT token.
    
    - **text**: Text to encode
    - **secret**: Secret key for signing
    - **algorithm**: Signing algorithm
    - **exp_minutes**: Expiration time in minutes
    
    Returns JWT token.
    """
    try:
        token = await service.encode(
            text,
            secret=secret,
            algorithm=algorithm,
            exp_minutes=exp_minutes
        )
        
        return JSONResponse(content={
            "token": token,
            "algorithm": algorithm,
            "expires_in_minutes": exp_minutes,
            "payload_type": "text"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JWT encoding failed: {str(e)}")


@jwt_encoder_router.post(
    "/file",
    summary="Encode file to JWT",
    description="Create JWT token from file content"
)
async def encode_file_to_jwt(
    file: UploadFile = File(...),
    secret: str = Form(default="your-secret-key", description="Secret key for signing"),
    algorithm: str = Query(default="HS256", description="Signing algorithm"),
    exp_minutes: Optional[int] = Query(default=None, description="Expiration time in minutes"),
    service: JWTEncoderService = Depends(get_jwt_encoder_service)
) -> StreamingResponse:
    """
    Encode file content to JWT token.
    
    - **file**: File to encode
    - **secret**: Secret key for signing
    - **algorithm**: Signing algorithm
    - **exp_minutes**: Expiration time in minutes
    
    Returns JWT token as downloadable file.
    """
    try:
        token = await service.encode_file(
            file,
            secret=secret,
            algorithm=algorithm,
            exp_minutes=exp_minutes
        )
        
        output_filename = service.get_output_filename(file.filename or "unknown")
        
        return StreamingResponse(
            iter([token.encode('utf-8')]),
            media_type="application/jwt",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JWT encoding failed: {str(e)}")


@jwt_encoder_router.get(
    "/algorithms",
    summary="List supported JWT algorithms",
    description="Get list of supported JWT signing algorithms"
)
async def get_jwt_algorithms() -> JSONResponse:
    """
    Get supported JWT algorithms.
    
    Returns list of supported signing algorithms.
    """
    return JSONResponse(content={
        "symmetric": {
            "HS256": "HMAC using SHA-256",
            "HS384": "HMAC using SHA-384", 
            "HS512": "HMAC using SHA-512"
        },
        "asymmetric": {
            "RS256": "RSASSA-PKCS1-v1_5 using SHA-256 (requires RSA key)",
            "RS384": "RSASSA-PKCS1-v1_5 using SHA-384 (requires RSA key)",
            "RS512": "RSASSA-PKCS1-v1_5 using SHA-512 (requires RSA key)",
            "ES256": "ECDSA using P-256 and SHA-256 (requires EC key)",
            "ES384": "ECDSA using P-384 and SHA-384 (requires EC key)",
            "ES512": "ECDSA using P-521 and SHA-512 (requires EC key)"
        },
        "recommended": "HS256",
        "note": "Asymmetric algorithms require proper key management"
    })


@jwt_encoder_router.get(
    "/info",
    summary="Get JWT encoder information",
    description="Get information about JWT encoding"
)
async def get_jwt_encoder_info(
    service: JWTEncoderService = Depends(get_jwt_encoder_service)
) -> JSONResponse:
    """
    Get JWT encoder information.
    
    Returns information about JWT encoding capabilities.
    """
    return JSONResponse(content={
        "encoder": "JWT (JSON Web Token)",
        "description": "Create signed JWT tokens for secure data transmission",
        "components": {
            "header": "Contains algorithm and token type",
            "payload": "Contains claims and data",
            "signature": "Verifies token integrity and authenticity"
        },
        "standard_claims": {
            "iss": "Issuer - who issued the token",
            "sub": "Subject - what the token is about", 
            "aud": "Audience - who the token is for",
            "exp": "Expiration - when token expires",
            "iat": "Issued At - when token was created",
            "nbf": "Not Before - token not valid before this time",
            "jti": "JWT ID - unique token identifier"
        },
        "use_cases": [
            "Authentication tokens",
            "API authorization",
            "Secure data exchange",
            "Single sign-on (SSO)",
            "Microservices communication"
        ],
        "security_notes": [
            "Use strong secret keys",
            "Keep secrets secure and rotate regularly", 
            "Set appropriate expiration times",
            "Validate tokens on receipt",
            "Use HTTPS in production"
        ]
    })