"""
Hex encoder service.
"""
import binascii
from typing import Union, BinaryIO
from fastapi import UploadFile

from .base_encoder import BaseEncoderService


class HexEncoderService(BaseEncoderService):
    """
    Service for Hexadecimal encoding operations.
    """
    
    def __init__(self):
        super().__init__()
        self.encoding_name = "hex"
    
    async def encode(
        self, 
        data: Union[str, bytes, BinaryIO, UploadFile], 
        **kwargs
    ) -> str:
        """
        Encode data to hexadecimal.
        
        Args:
            data: Input data to encode
            **kwargs: Additional parameters
                - uppercase: Use uppercase hex digits (default: False)
                - separator: Separator between hex bytes (default: '')
                - prefix: Prefix for hex output (default: '')
                
        Returns:
            Hexadecimal encoded string
        """
        if not self.validate_input(data):
            raise ValueError("Invalid input data")
        
        if isinstance(data, UploadFile):
            return await self.encode_file(data, **kwargs)
        
        # Prepare data as bytes
        byte_data = self._prepare_data(data)
        
        # Get encoding parameters
        uppercase = kwargs.get('uppercase', False)
        separator = kwargs.get('separator', '')
        prefix = kwargs.get('prefix', '')
        
        # Encode to hex
        hex_string = binascii.hexlify(byte_data).decode('ascii')
        
        # Apply formatting
        if uppercase:
            hex_string = hex_string.upper()
        
        # Add separator between bytes
        if separator:
            hex_pairs = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
            hex_string = separator.join(hex_pairs)
        
        # Add prefix
        if prefix:
            if separator:
                hex_parts = hex_string.split(separator)
                hex_string = separator.join([prefix + part for part in hex_parts])
            else:
                hex_string = prefix + hex_string
        
        return hex_string
    
    async def encode_file(
        self, 
        file: UploadFile, 
        **kwargs
    ) -> str:
        """
        Encode file content to hexadecimal.
        
        Args:
            file: Input file to encode
            **kwargs: Additional parameters
                
        Returns:
            Hexadecimal encoded string
        """
        content = await self._read_file_content(file)
        return await self.encode(content, **kwargs)
    
    async def encode_ascii_hex(self, text: str, **kwargs) -> str:
        """
        Encode ASCII text to hex representation.
        
        Args:
            text: ASCII text to encode
            **kwargs: Additional parameters
                
        Returns:
            Hex encoded ASCII string
        """
        return await self.encode(text.encode('ascii'), **kwargs)
    
    async def encode_with_length(self, data: Union[str, bytes], **kwargs) -> str:
        """
        Encode data with length prefix.
        
        Args:
            data: Data to encode
            **kwargs: Additional parameters
                
        Returns:
            Length-prefixed hex string
        """
        if isinstance(data, str):
            byte_data = data.encode('utf-8')
        else:
            byte_data = data
        
        length = len(byte_data)
        length_hex = f"{length:04x}"
        
        encoded = await self.encode(byte_data, **kwargs)
        return f"{length_hex}{encoded}"
    
    def get_output_filename(self, original_filename: str, **kwargs) -> str:
        """
        Generate output filename for hex encoded data.
        
        Args:
            original_filename: Original filename
            **kwargs: Additional parameters
            
        Returns:
            Generated output filename
        """
        if not original_filename or original_filename == "unknown":
            return "encoded.hex"
        
        return f"{original_filename}.hex"
    
    def validate_input(self, data) -> bool:
        """
        Validate input data for hex encoding.
        
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
        
        if hasattr(data, 'read'):
            return True
        
        return False


# Dependency injection
def get_hex_encoder_service() -> HexEncoderService:
    """
    Dependency injection for HexEncoderService.
    
    Returns:
        HexEncoderService instance
    """
    return HexEncoderService()