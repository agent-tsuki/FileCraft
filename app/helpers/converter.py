from fastapi import UploadFile
import base64
import zlib
from typing import AsyncGenerator


class Base64FileStreamer:
    def __init__(
            self, file: UploadFile, max_size: int,
            compress: bool, chunk_size: int = 8192
    ):
        self.file = file
        self.max_size = max_size
        self.chunk_size = chunk_size
        self.compress = compress
        self.total_read = 0
        self.compressor = zlib.compressobj() if compress else None

    async def __aiter__(self) -> AsyncGenerator[bytes, None]:
        try:
            while True:
                chunk = await self.file.read(self.chunk_size)
                if not chunk:
                    break

                self.total_read += len(chunk)
                if self.total_read > self.max_size:
                    raise ValueError("File too large")

                if self.compress:
                    chunk = self.compressor.compress(chunk)

                yield base64.b64encode(chunk)

            if self.compress:
                yield base64.b64encode(self.compressor.flush())
        finally:
            await self.file.close()  # Safe cleanup
