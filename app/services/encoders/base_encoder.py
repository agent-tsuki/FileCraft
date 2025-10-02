"""
Base encoder service class.
"""

from abc import ABC, abstractmethod
from typing import Union, BinaryIO, Any, Dict, Optional
from fastapi import UploadFile
import io


class BaseEncoderService(ABC):
    """
    Abstract base class for all encoder services.
    """

    def __init__(self):
        self.encoding_name = self.__class__.__name__.replace(
            "EncoderService", ""
        ).lower()

    @abstractmethod
    async def encode(
        self, data: Union[str, bytes, BinaryIO, UploadFile], **kwargs
    ) -> Union[str, bytes]:
        """
        Abstract method to encode data.

        Args:
            data: Input data to encode
            **kwargs: Additional encoding parameters

        Returns:
            Encoded data
        """
        pass

    @abstractmethod
    async def encode_file(self, file: UploadFile, **kwargs) -> Union[str, bytes]:
        """
        Abstract method to encode file data.

        Args:
            file: Input file to encode
            **kwargs: Additional encoding parameters

        Returns:
            Encoded file data
        """
        pass

    async def encode_stream(
        self, data: Union[str, bytes, BinaryIO, UploadFile], **kwargs
    ):
        """
        Encode data as a stream.

        Args:
            data: Input data to encode
            **kwargs: Additional encoding parameters

        Yields:
            Chunks of encoded data
        """
        encoded_data = await self.encode(data, **kwargs)

        if isinstance(encoded_data, str):
            encoded_data = encoded_data.encode("utf-8")

        chunk_size = kwargs.get("chunk_size", 8192)
        stream = io.BytesIO(encoded_data)

        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            yield chunk

    def get_output_filename(self, original_filename: str, **kwargs) -> str:
        """
        Generate output filename for encoded data.

        Args:
            original_filename: Original filename
            **kwargs: Additional parameters

        Returns:
            Generated output filename
        """
        if not original_filename or original_filename == "unknown":
            return f"encoded.{self.encoding_name}"

        return f"{original_filename}.{self.encoding_name}"

    def get_content_type(self) -> str:
        """
        Get the content type for encoded data.

        Returns:
            Content type string
        """
        return "text/plain"

    def validate_input(self, data: Any) -> bool:
        """
        Validate input data.

        Args:
            data: Input data to validate

        Returns:
            True if valid, False otherwise
        """
        return data is not None

    async def _read_file_content(self, file: UploadFile) -> bytes:
        """
        Helper method to read file content.

        Args:
            file: UploadFile instance

        Returns:
            File content as bytes
        """
        await file.seek(0)
        content = await file.read()
        await file.seek(0)  # Reset for potential reuse
        return content

    def _prepare_data(self, data: Union[str, bytes, BinaryIO]) -> bytes:
        """
        Helper method to prepare data for encoding.

        Args:
            data: Input data

        Returns:
            Data as bytes
        """
        if isinstance(data, str):
            return data.encode("utf-8")
        elif isinstance(data, bytes):
            return data
        elif hasattr(data, "read"):
            return data.read()
        else:
            raise ValueError("Unsupported data type")
