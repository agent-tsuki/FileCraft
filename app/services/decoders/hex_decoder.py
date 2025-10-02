"""
Hex decoder service.
"""

import binascii
import re
from typing import Union, BinaryIO
from fastapi import UploadFile, HTTPException

from .base_decoder import BaseDecoderService


class HexDecoderService(BaseDecoderService):
    """
    Service for Hexadecimal decoding operations.
    """

    def __init__(self):
        super().__init__()
        self.decoding_name = "hex"

    async def decode(
        self, data: Union[str, bytes, BinaryIO, UploadFile], **kwargs
    ) -> bytes:
        """
        Decode hexadecimal data.

        Args:
            data: Input hex data to decode
            **kwargs: Additional parameters
                - ignore_whitespace: Ignore whitespace in hex (default: True)
                - ignore_separators: Ignore common separators (default: True)
                - strict: Strict hex validation (default: False)

        Returns:
            Decoded bytes
        """
        if not self.validate_input(data):
            raise ValueError("Invalid input data")

        if isinstance(data, UploadFile):
            return await self.decode_file(data, **kwargs)

        # Prepare data as string
        string_data = self._prepare_data(data)
        if isinstance(string_data, bytes):
            string_data = string_data.decode("utf-8")

        # Clean the hex string
        cleaned_hex = self._clean_hex_string(string_data, **kwargs)

        # Validate hex format
        if kwargs.get("strict", False) and not self._is_valid_hex(cleaned_hex):
            raise HTTPException(status_code=400, detail="Invalid hexadecimal format")

        try:
            # Decode the hex string
            decoded_bytes = binascii.unhexlify(cleaned_hex)
            return decoded_bytes

        except (binascii.Error, ValueError) as e:
            raise HTTPException(
                status_code=400, detail=f"Hex decoding failed: {str(e)}"
            )

    async def decode_file(self, file: UploadFile, **kwargs) -> bytes:
        """
        Decode hex file content.

        Args:
            file: Input file containing hex data
            **kwargs: Additional parameters

        Returns:
            Decoded bytes
        """
        content = await self._read_file_content(file)
        string_data = content.decode("utf-8", errors="replace")

        return await self.decode(string_data, **kwargs)

    async def decode_to_text(
        self, hex_data: str, encoding: str = "utf-8", **kwargs
    ) -> str:
        """
        Decode hex data to text.

        Args:
            hex_data: Hex string to decode
            encoding: Text encoding (default: utf-8)
            **kwargs: Additional parameters

        Returns:
            Decoded text string
        """
        try:
            byte_data = await self.decode(hex_data, **kwargs)
            return byte_data.decode(encoding, errors="replace")
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Hex to text decoding failed: {str(e)}"
            )

    def decode_with_length_prefix(self, hex_data: str, **kwargs) -> bytes:
        """
        Decode hex data with length prefix.

        Args:
            hex_data: Length-prefixed hex string
            **kwargs: Additional parameters

        Returns:
            Decoded bytes
        """
        cleaned_hex = self._clean_hex_string(hex_data, **kwargs)

        if len(cleaned_hex) < 4:
            raise HTTPException(
                status_code=400, detail="Invalid length-prefixed hex data"
            )

        try:
            # Extract length (first 4 hex characters = 2 bytes)
            length_hex = cleaned_hex[:4]
            expected_length = int(length_hex, 16)

            # Extract data portion
            data_hex = cleaned_hex[4:]

            # Validate length
            expected_hex_length = expected_length * 2
            if len(data_hex) != expected_hex_length:
                raise HTTPException(
                    status_code=400,
                    detail=f"Length mismatch: expected {expected_hex_length} hex chars, got {len(data_hex)}",
                )

            # Decode data
            return binascii.unhexlify(data_hex)

        except ValueError as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid length prefix: {str(e)}"
            )

    def _clean_hex_string(self, hex_string: str, **kwargs) -> str:
        """
        Clean hex string by removing unwanted characters.

        Args:
            hex_string: Raw hex string
            **kwargs: Additional parameters

        Returns:
            Cleaned hex string
        """
        cleaned = hex_string.strip()

        # Remove whitespace if requested
        if kwargs.get("ignore_whitespace", True):
            cleaned = re.sub(r"\s+", "", cleaned)

        # Remove common separators if requested
        if kwargs.get("ignore_separators", True):
            # Remove common separators: : - _ space
            cleaned = re.sub(r"[:\-_\s]", "", cleaned)

        # Remove common prefixes
        if cleaned.startswith("0x") or cleaned.startswith("0X"):
            cleaned = cleaned[2:]

        # Remove \x prefixes (like \x41\x42)
        cleaned = re.sub(r"\\x", "", cleaned)

        return cleaned

    def _is_valid_hex(self, hex_string: str) -> bool:
        """
        Validate if string contains only hex characters.

        Args:
            hex_string: String to validate

        Returns:
            True if valid hex, False otherwise
        """
        if len(hex_string) % 2 != 0:
            return False

        return re.match(r"^[0-9A-Fa-f]+$", hex_string) is not None

    def validate_input(self, data) -> bool:
        """
        Validate input data for hex decoding.

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
        Generate output filename for decoded hex data.

        Args:
            original_filename: Original filename
            **kwargs: Additional parameters

        Returns:
            Generated output filename
        """
        if not original_filename or original_filename == "unknown":
            return "decoded.bin"

        # Remove hex extension
        if original_filename.endswith(".hex"):
            return original_filename[:-4]

        return f"{original_filename}.decoded"

    def get_content_type(self, **kwargs) -> str:
        """
        Get content type for decoded hex data.

        Args:
            **kwargs: Additional parameters

        Returns:
            Content type string
        """
        return kwargs.get("content_type", "application/octet-stream")


# Dependency injection
def get_hex_decoder_service() -> HexDecoderService:
    """
    Dependency injection for HexDecoderService.

    Returns:
        HexDecoderService instance
    """
    return HexDecoderService()
