"""
URL encoder service.
"""

import urllib.parse
from typing import Union, BinaryIO
from fastapi import UploadFile

from .base_encoder import BaseEncoderService


class URLEncoderService(BaseEncoderService):
    """
    Service for URL encoding operations.
    """

    def __init__(self):
        super().__init__()
        self.encoding_name = "url"

    async def encode(
        self, data: Union[str, bytes, BinaryIO, UploadFile], **kwargs
    ) -> str:
        """
        Encode data for URL.

        Args:
            data: Input data to encode
            **kwargs: Additional parameters
                - safe: Characters to not encode (default: '')
                - encoding: Character encoding (default: 'utf-8')
                - quote_via: Quoting function (default: urllib.parse.quote)

        Returns:
            URL encoded string
        """
        if not self.validate_input(data):
            raise ValueError("Invalid input data")

        if isinstance(data, UploadFile):
            return await self.encode_file(data, **kwargs)

        # Prepare data as string
        if isinstance(data, bytes):
            encoding = kwargs.get("encoding", "utf-8")
            string_data = data.decode(encoding)
        elif hasattr(data, "read"):
            content = data.read()
            if isinstance(content, bytes):
                encoding = kwargs.get("encoding", "utf-8")
                string_data = content.decode(encoding)
            else:
                string_data = content
        else:
            string_data = str(data)

        # Get encoding parameters
        safe = kwargs.get("safe", "")
        encoding = kwargs.get("encoding", "utf-8")

        # Encode the string
        encoded = urllib.parse.quote(string_data, safe=safe, encoding=encoding)

        return encoded

    async def encode_file(self, file: UploadFile, **kwargs) -> str:
        """
        Encode file content for URL.

        Args:
            file: Input file to encode
            **kwargs: Additional parameters

        Returns:
            URL encoded string
        """
        content = await self._read_file_content(file)

        encoding = kwargs.get("encoding", "utf-8")
        string_data = content.decode(encoding, errors="replace")

        return await self.encode(string_data, **kwargs)

    def encode_query_params(self, params: dict, **kwargs) -> str:
        """
        Encode dictionary as URL query parameters.

        Args:
            params: Dictionary of parameters
            **kwargs: Additional parameters
                - doseq: Handle sequences in values (default: False)
                - safe: Characters to not encode (default: '')
                - encoding: Character encoding (default: 'utf-8')

        Returns:
            URL encoded query string
        """
        doseq = kwargs.get("doseq", False)
        safe = kwargs.get("safe", "")
        encoding = kwargs.get("encoding", "utf-8")

        return urllib.parse.urlencode(params, doseq=doseq, safe=safe, encoding=encoding)

    def encode_plus(self, data: str, **kwargs) -> str:
        """
        Encode using quote_plus (spaces become +).

        Args:
            data: String data to encode
            **kwargs: Additional parameters

        Returns:
            URL encoded string with + for spaces
        """
        safe = kwargs.get("safe", "")
        encoding = kwargs.get("encoding", "utf-8")

        return urllib.parse.quote_plus(data, safe=safe, encoding=encoding)

    def get_output_filename(self, original_filename: str, **kwargs) -> str:
        """
        Generate output filename for URL encoded data.

        Args:
            original_filename: Original filename
            **kwargs: Additional parameters

        Returns:
            Generated output filename
        """
        if not original_filename or original_filename == "unknown":
            return "encoded.url"

        return f"{original_filename}.url"

    def validate_input(self, data) -> bool:
        """
        Validate input data for URL encoding.

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
def get_url_encoder_service() -> URLEncoderService:
    """
    Dependency injection for URLEncoderService.

    Returns:
        URLEncoderService instance
    """
    return URLEncoderService()
