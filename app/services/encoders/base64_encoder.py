"""
Base64 encoder service.
"""

import base64
from typing import Union, BinaryIO
from fastapi import UploadFile

from .base_encoder import BaseEncoderService


class Base64EncoderService(BaseEncoderService):
    """
    Service for Base64 encoding operations.
    """

    def __init__(self):
        super().__init__()
        self.encoding_name = "b64"

    async def encode(
        self, data: Union[str, bytes, BinaryIO, UploadFile], **kwargs
    ) -> str:
        """
        Encode data to Base64.

        Args:
            data: Input data to encode
            **kwargs: Additional parameters
                - url_safe: Use URL-safe Base64 encoding (default: False)

        Returns:
            Base64 encoded string
        """
        if not self.validate_input(data):
            raise ValueError("Invalid input data")

        if isinstance(data, UploadFile):
            return await self.encode_file(data, **kwargs)

        # Prepare data as bytes
        byte_data = self._prepare_data(data)

        # Choose encoding method
        url_safe = kwargs.get("url_safe", False)

        if url_safe:
            encoded_bytes = base64.urlsafe_b64encode(byte_data)
        else:
            encoded_bytes = base64.b64encode(byte_data)

        return encoded_bytes.decode("ascii")

    async def encode_file(self, file: UploadFile, **kwargs) -> str:
        """
        Encode file content to Base64.

        Args:
            file: Input file to encode
            **kwargs: Additional parameters
                - url_safe: Use URL-safe Base64 encoding (default: False)

        Returns:
            Base64 encoded string
        """
        content = await self._read_file_content(file)

        url_safe = kwargs.get("url_safe", False)

        if url_safe:
            encoded_bytes = base64.urlsafe_b64encode(content)
        else:
            encoded_bytes = base64.b64encode(content)

        return encoded_bytes.decode("ascii")

    def get_output_filename(self, original_filename: str, **kwargs) -> str:
        """
        Generate output filename for Base64 encoded data.

        Args:
            original_filename: Original filename
            **kwargs: Additional parameters
                - url_safe: If URL-safe encoding is used

        Returns:
            Generated output filename
        """
        if not original_filename or original_filename == "unknown":
            return "encoded.b64"

        url_safe = kwargs.get("url_safe", False)
        extension = "b64url" if url_safe else "b64"

        return f"{original_filename}.{extension}"

    def validate_input(self, data) -> bool:
        """
        Validate input data for Base64 encoding.

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
            return True

        if hasattr(data, "read"):
            return True

        return False


# Dependency injection
def get_base64_encoder_service() -> Base64EncoderService:
    """
    Dependency injection for Base64EncoderService.

    Returns:
        Base64EncoderService instance
    """
    return Base64EncoderService()
