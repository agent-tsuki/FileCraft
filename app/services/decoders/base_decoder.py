"""
Base decoder service class.
"""
from abc import ABC, abstractmethod
from typing import Union, BinaryIO, Any, Dict, Optional
from fastapi import UploadFile
import io


class BaseDecoderService(ABC):
    """
    Abstract base class for all decoder services.
    """
    
    def __init__(self):
        self.decoding_name = self.__class__.__name__.replace("DecoderService", "").lower()
    
    @abstractmethod
    async def decode(
        self, 
        data: Union[str, bytes, BinaryIO, UploadFile], 
        **kwargs
    ) -> Union[str, bytes]:
        """
        Abstract method to decode data.
        
        Args:
            data: Input data to decode
            **kwargs: Additional decoding parameters
            
        Returns:
            Decoded data
        """
        pass
    
    @abstractmethod
    async def decode_file(
        self, 
        file: UploadFile, 
        **kwargs
    ) -> Union[str, bytes]:
        """
        Abstract method to decode file data.
        
        Args:
            file: Input file to decode
            **kwargs: Additional decoding parameters
            
        Returns:
            Decoded file data
        """
        pass
    
    async def decode_stream(
        self, 
        data: Union[str, bytes, BinaryIO, UploadFile], 
        **kwargs
    ):
        """
        Decode data as a stream.
        
        Args:
            data: Input data to decode
            **kwargs: Additional decoding parameters
            
        Yields:
            Chunks of decoded data
        """
        decoded_data = await self.decode(data, **kwargs)
        
        if isinstance(decoded_data, str):
            decoded_data = decoded_data.encode('utf-8')
            
        chunk_size = kwargs.get('chunk_size', 8192)
        stream = io.BytesIO(decoded_data)
        
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            yield chunk
    
    def get_output_filename(self, original_filename: str, **kwargs) -> str:
        """
        Generate output filename for decoded data.
        
        Args:
            original_filename: Original filename
            **kwargs: Additional parameters
            
        Returns:
            Generated output filename
        """
        if not original_filename or original_filename == "unknown":
            return "decoded"
        
        # Remove encoding extension if present
        if original_filename.endswith(f".{self.decoding_name}"):
            return original_filename[:-len(f".{self.decoding_name}")]
        
        return f"{original_filename}.decoded"
    
    def get_content_type(self, **kwargs) -> str:
        """
        Get the content type for decoded data.
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            Content type string
        """
        return kwargs.get('content_type', 'application/octet-stream')
    
    def validate_input(self, data: Any) -> bool:
        """
        Validate input data for decoding.
        
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
    
    def _prepare_data(self, data: Union[str, bytes, BinaryIO]) -> Union[str, bytes]:
        """
        Helper method to prepare data for decoding.
        
        Args:
            data: Input data
            
        Returns:
            Data as string or bytes
        """
        if isinstance(data, str):
            return data
        elif isinstance(data, bytes):
            try:
                return data.decode('utf-8')
            except UnicodeDecodeError:
                return data
        elif hasattr(data, 'read'):
            content = data.read()
            if isinstance(content, bytes):
                try:
                    return content.decode('utf-8')
                except UnicodeDecodeError:
                    return content
            return content
        else:
            raise ValueError("Unsupported data type")