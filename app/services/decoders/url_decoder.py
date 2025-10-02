"""
URL decoder service.
"""

import urllib.parse
from typing import Union, BinaryIO
from fastapi import UploadFile, HTTPException

from .base_decoder import BaseDecoderService


class URLDecoderService(BaseDecoderService):
    """
    Service for URL decoding operations.
    """

    def __init__(self):
        super().__init__()
        self.decoding_name = "url"

    async def decode(
        self, data: Union[str, bytes, BinaryIO, UploadFile], **kwargs
    ) -> str:
        """
        Decode URL encoded data.

        Args:
            data: Input URL encoded data to decode
            **kwargs: Additional parameters
                - encoding: Character encoding (default: 'utf-8')
                - errors: Error handling (default: 'replace')

        Returns:
            Decoded string
        """
        if not self.validate_input(data):
            raise ValueError("Invalid input data")

        if isinstance(data, UploadFile):
            return await self.decode_file(data, **kwargs)

        # Prepare data as string
        string_data = self._prepare_data(data)
        if isinstance(string_data, bytes):
            encoding = kwargs.get("encoding", "utf-8")
            string_data = string_data.decode(encoding)

        # Get decoding parameters
        encoding = kwargs.get("encoding", "utf-8")
        errors = kwargs.get("errors", "replace")

        try:
            # Decode the URL encoded string
            decoded = urllib.parse.unquote(
                string_data, encoding=encoding, errors=errors
            )
            return decoded

        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"URL decoding failed: {str(e)}"
            )

    async def decode_file(self, file: UploadFile, **kwargs) -> str:
        """
        Decode URL encoded file content.

        Args:
            file: Input file containing URL encoded data
            **kwargs: Additional parameters

        Returns:
            Decoded string
        """
        content = await self._read_file_content(file)

        encoding = kwargs.get("encoding", "utf-8")
        string_data = content.decode(encoding, errors="replace")

        return await self.decode(string_data, **kwargs)

    def decode_query_params(self, query_string: str, **kwargs) -> dict:
        """
        Decode URL query parameters.

        Args:
            query_string: URL query string
            **kwargs: Additional parameters
                - keep_blank_values: Keep blank values (default: False)
                - strict_parsing: Strict parsing (default: False)
                - encoding: Character encoding (default: 'utf-8')
                - max_num_fields: Max number of fields (default: None)

        Returns:
            Dictionary of decoded parameters
        """
        keep_blank_values = kwargs.get("keep_blank_values", False)
        strict_parsing = kwargs.get("strict_parsing", False)
        encoding = kwargs.get("encoding", "utf-8")
        max_num_fields = kwargs.get("max_num_fields", None)

        try:
            parsed = urllib.parse.parse_qs(
                query_string,
                keep_blank_values=keep_blank_values,
                strict_parsing=strict_parsing,
                encoding=encoding,
                max_num_fields=max_num_fields,
            )

            # Convert single-item lists to strings for convenience
            result = {}
            for key, value_list in parsed.items():
                if len(value_list) == 1:
                    result[key] = value_list[0]
                else:
                    result[key] = value_list

            return result

        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Query parameter decoding failed: {str(e)}"
            )

    def decode_plus(self, data: str, **kwargs) -> str:
        """
        Decode URL encoded data with + as spaces.

        Args:
            data: URL encoded string with + for spaces
            **kwargs: Additional parameters

        Returns:
            Decoded string
        """
        encoding = kwargs.get("encoding", "utf-8")
        errors = kwargs.get("errors", "replace")

        try:
            return urllib.parse.unquote_plus(data, encoding=encoding, errors=errors)
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"URL+ decoding failed: {str(e)}"
            )

    def parse_url(self, url: str) -> dict:
        """
        Parse URL into components.

        Args:
            url: URL to parse

        Returns:
            Dictionary with URL components
        """
        try:
            parsed = urllib.parse.urlparse(url)
            return {
                "scheme": parsed.scheme,
                "netloc": parsed.netloc,
                "path": parsed.path,
                "params": parsed.params,
                "query": parsed.query,
                "fragment": parsed.fragment,
                "username": parsed.username,
                "password": parsed.password,
                "hostname": parsed.hostname,
                "port": parsed.port,
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"URL parsing failed: {str(e)}")

    def validate_input(self, data) -> bool:
        """
        Validate input data for URL decoding.

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
            return len(str(data).strip()) > 0

        if hasattr(data, "read"):
            return True

        return False

    def get_output_filename(self, original_filename: str, **kwargs) -> str:
        """
        Generate output filename for decoded URL data.

        Args:
            original_filename: Original filename
            **kwargs: Additional parameters

        Returns:
            Generated output filename
        """
        if not original_filename or original_filename == "unknown":
            return "decoded.txt"

        # Remove URL extension
        if original_filename.endswith(".url"):
            return original_filename[:-4]

        return f"{original_filename}.decoded"


# Dependency injection
def get_url_decoder_service() -> URLDecoderService:
    """
    Dependency injection for URLDecoderService.

    Returns:
        URLDecoderService instance
    """
    return URLDecoderService()
