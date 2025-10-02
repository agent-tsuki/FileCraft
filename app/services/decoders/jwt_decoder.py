"""
JWT decoder service.
"""

import jwt
import json
import base64
from typing import Union, BinaryIO, Dict, Any, Optional
from fastapi import UploadFile, HTTPException

from .base_decoder import BaseDecoderService


class JWTDecoderService(BaseDecoderService):
    """
    Service for JWT decoding operations.
    """

    def __init__(self):
        super().__init__()
        self.decoding_name = "jwt"
        self.default_algorithm = "HS256"
        self.default_secret = "your-secret-key"  # Should be configurable

    async def decode(
        self, data: Union[str, bytes, BinaryIO, UploadFile], **kwargs
    ) -> Union[Dict[str, Any], bytes]:
        """
        Decode JWT token.

        Args:
            data: Input JWT token to decode
            **kwargs: Additional parameters
                - secret: Secret key for verification (default: configured secret)
                - algorithm: Expected algorithm (default: HS256)
                - verify: Verify signature (default: True)
                - verify_exp: Verify expiration (default: True)
                - audience: Expected audience (default: None)
                - issuer: Expected issuer (default: None)
                - options: JWT decode options (default: None)

        Returns:
            Decoded payload
        """
        if not self.validate_input(data):
            raise ValueError("Invalid input data")

        if isinstance(data, UploadFile):
            return await self.decode_file(data, **kwargs)

        # Prepare token string
        token = self._prepare_data(data)
        if isinstance(token, bytes):
            token = token.decode("utf-8")

        # Clean the token
        token = token.strip()

        # Get decoding parameters
        secret = kwargs.get("secret", self.default_secret)
        algorithm = kwargs.get("algorithm", self.default_algorithm)
        verify = kwargs.get("verify", True)

        # Prepare decode options
        options = kwargs.get("options", {})
        if not kwargs.get("verify_exp", True):
            options["verify_exp"] = False

        try:
            if verify:
                payload = jwt.decode(
                    token,
                    secret,
                    algorithms=[algorithm],
                    audience=kwargs.get("audience"),
                    issuer=kwargs.get("issuer"),
                    options=options,
                )
            else:
                # Decode without verification
                payload = jwt.decode(token, options={"verify_signature": False})

            # If payload contains base64 encoded data, try to decode it
            if isinstance(payload, dict) and "data" in payload:
                data_value = payload["data"]
                if isinstance(data_value, str):
                    try:
                        # Check if it's base64 encoded binary data
                        decoded_data = base64.b64decode(data_value)
                        # If it's binary data and we want raw output, return it
                        if kwargs.get("raw_output", False):
                            return decoded_data
                        # Otherwise, keep it in the payload
                    except Exception:
                        pass  # Not base64, keep as is

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="JWT token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JWT token: {str(e)}")
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"JWT decoding failed: {str(e)}"
            )

    async def decode_file(
        self, file: UploadFile, **kwargs
    ) -> Union[Dict[str, Any], bytes]:
        """
        Decode JWT token from file.

        Args:
            file: Input file containing JWT token
            **kwargs: Additional JWT parameters

        Returns:
            Decoded payload
        """
        content = await self._read_file_content(file)
        token = content.decode("utf-8").strip()

        return await self.decode(token, **kwargs)

    def decode_header(self, token: str) -> Dict[str, Any]:
        """
        Decode JWT header without verification.

        Args:
            token: JWT token

        Returns:
            JWT header
        """
        try:
            return jwt.get_unverified_header(token)
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Failed to decode JWT header: {str(e)}"
            )

    def validate_token_format(self, token: str) -> bool:
        """
        Validate JWT token format.

        Args:
            token: JWT token to validate

        Returns:
            True if format is valid, False otherwise
        """
        parts = token.split(".")
        return len(parts) == 3

    def get_token_info(self, token: str) -> Dict[str, Any]:
        """
        Get information about JWT token without full decoding.

        Args:
            token: JWT token

        Returns:
            Token information
        """
        if not self.validate_token_format(token):
            raise HTTPException(status_code=400, detail="Invalid JWT format")

        try:
            header = self.decode_header(token)

            # Try to decode payload without verification to get basic info
            payload = jwt.decode(token, options={"verify_signature": False})

            return {
                "header": header,
                "payload_keys": (
                    list(payload.keys()) if isinstance(payload, dict) else []
                ),
                "has_expiration": (
                    "exp" in payload if isinstance(payload, dict) else False
                ),
                "algorithm": header.get("alg"),
                "token_type": header.get("typ", "JWT"),
            }
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Failed to get token info: {str(e)}"
            )

    def validate_input(self, data) -> bool:
        """
        Validate input data for JWT decoding.

        Args:
            data: Input data to validate

        Returns:
            True if valid, False otherwise
        """
        if data is None:
            return False

        if isinstance(data, UploadFile):
            return True

        if isinstance(data, (str, bytes)):
            token_str = str(data).strip()
            return len(token_str) > 0 and self.validate_token_format(token_str)

        if hasattr(data, "read"):
            return True

        return False

    def get_output_filename(self, original_filename: str, **kwargs) -> str:
        """
        Generate output filename for decoded JWT.

        Args:
            original_filename: Original filename
            **kwargs: Additional parameters

        Returns:
            Generated output filename
        """
        if not original_filename or original_filename == "unknown":
            return "decoded.json"

        # Remove JWT extension
        if original_filename.endswith(".jwt"):
            base_name = original_filename[:-4]
        else:
            base_name = original_filename

        return f"{base_name}.json"

    def get_content_type(self, **kwargs) -> str:
        """
        Get content type for decoded JWT.

        Args:
            **kwargs: Additional parameters

        Returns:
            Content type string
        """
        if kwargs.get("raw_output", False):
            return "application/octet-stream"
        return "application/json"


# Dependency injection
def get_jwt_decoder_service() -> JWTDecoderService:
    """
    Dependency injection for JWTDecoderService.

    Returns:
        JWTDecoderService instance
    """
    return JWTDecoderService()
