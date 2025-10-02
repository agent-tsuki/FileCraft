"""
JWT encoder service.
"""

import jwt
import json
from datetime import datetime, timedelta, timezone
from typing import Union, BinaryIO, Dict, Any, Optional
from fastapi import UploadFile, HTTPException

from .base_encoder import BaseEncoderService


class JWTEncoderService(BaseEncoderService):
    """
    Service for JWT encoding operations.
    """

    def __init__(self):
        super().__init__()
        self.encoding_name = "jwt"
        self.default_algorithm = "HS256"
        self.default_secret = "your-secret-key"  # Should be configurable

    async def encode(
        self, data: Union[str, bytes, BinaryIO, UploadFile, Dict], **kwargs
    ) -> str:
        """
        Encode data as JWT token.

        Args:
            data: Input data to encode (payload)
            **kwargs: Additional parameters
                - secret: Secret key for signing (default: configured secret)
                - algorithm: Signing algorithm (default: HS256)
                - exp_minutes: Expiration time in minutes (default: None)
                - issuer: JWT issuer (default: None)
                - audience: JWT audience (default: None)
                - subject: JWT subject (default: None)

        Returns:
            JWT token string
        """
        if not self.validate_input(data):
            raise ValueError("Invalid input data")

        if isinstance(data, UploadFile):
            return await self.encode_file(data, **kwargs)

        # Prepare payload
        payload = await self._prepare_payload(data, **kwargs)

        # Get encoding parameters
        secret = kwargs.get("secret", self.default_secret)
        algorithm = kwargs.get("algorithm", self.default_algorithm)

        # Add standard claims
        payload = self._add_standard_claims(payload, **kwargs)

        try:
            token = jwt.encode(payload, secret, algorithm=algorithm)
            return token
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"JWT encoding failed: {str(e)}"
            )

    async def encode_file(self, file: UploadFile, **kwargs) -> str:
        """
        Encode file content as JWT token.

        Args:
            file: Input file to encode
            **kwargs: Additional JWT parameters

        Returns:
            JWT token string
        """
        content = await self._read_file_content(file)

        # Try to parse as JSON first, otherwise use as string
        try:
            payload = json.loads(content.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # If not valid JSON, encode the content as base64 in payload
            import base64

            payload = {
                "data": base64.b64encode(content).decode("ascii"),
                "filename": file.filename,
                "content_type": file.content_type,
            }

        return await self.encode(payload, **kwargs)

    async def _prepare_payload(self, data: Any, **kwargs) -> Dict[str, Any]:
        """
        Prepare payload for JWT encoding.

        Args:
            data: Input data
            **kwargs: Additional parameters

        Returns:
            Prepared payload dictionary
        """
        if isinstance(data, dict):
            return data.copy()

        if isinstance(data, str):
            try:
                # Try to parse as JSON
                return json.loads(data)
            except json.JSONDecodeError:
                # If not JSON, wrap in payload
                return {"data": data}

        if isinstance(data, bytes):
            try:
                # Try to decode and parse as JSON
                decoded = data.decode("utf-8")
                return json.loads(decoded)
            except (UnicodeDecodeError, json.JSONDecodeError):
                # If not JSON, encode as base64
                import base64

                return {"data": base64.b64encode(data).decode("ascii")}

        # For other types, convert to string representation
        return {"data": str(data)}

    def _add_standard_claims(self, payload: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Add standard JWT claims to payload.

        Args:
            payload: Base payload
            **kwargs: Additional parameters

        Returns:
            Payload with standard claims
        """
        # Add expiration if specified
        exp_minutes = kwargs.get("exp_minutes")
        if exp_minutes:
            payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)

        # Add issued at
        payload["iat"] = datetime.now(timezone.utc)

        # Add other standard claims if provided
        if kwargs.get("issuer"):
            payload["iss"] = kwargs["issuer"]

        if kwargs.get("audience"):
            payload["aud"] = kwargs["audience"]

        if kwargs.get("subject"):
            payload["sub"] = kwargs["subject"]

        return payload

    def get_output_filename(self, original_filename: str, **kwargs) -> str:
        """
        Generate output filename for JWT token.

        Args:
            original_filename: Original filename
            **kwargs: Additional parameters

        Returns:
            Generated output filename
        """
        if not original_filename or original_filename == "unknown":
            return "token.jwt"

        return f"{original_filename}.jwt"

    def get_content_type(self) -> str:
        """
        Get content type for JWT token.

        Returns:
            Content type string
        """
        return "application/jwt"

    def validate_input(self, data) -> bool:
        """
        Validate input data for JWT encoding.

        Args:
            data: Input data to validate

        Returns:
            True if valid, False otherwise
        """
        if data is None:
            return False

        # JWT can encode various types of data
        return True


# Dependency injection
def get_jwt_encoder_service() -> JWTEncoderService:
    """
    Dependency injection for JWTEncoderService.

    Returns:
        JWTEncoderService instance
    """
    return JWTEncoderService()
