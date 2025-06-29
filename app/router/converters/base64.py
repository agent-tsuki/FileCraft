from fastapi import APIRouter, UploadFile, status, Query
from fastapi.responses import JSONResponse, StreamingResponse

from base64 import b64encode
import zlib
import io

from app.helpers.file_validator import validate_file_size, get_file_type
from app.helpers.constants import MAX_UPLOAD_SIZE

base64Router = APIRouter(prefix="/base63")


@base64Router.post("/file")
async def convert_img_to_base64(
    file: UploadFile,
    compress: bool = Query(default=False)
):
    if not file.filename:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": False,
                "message": "File is empty or without filename"
            }
        )

    content = await file.read()
    _, exe = get_file_type(file.filename)

    if not validate_file_size(len(content), exe):  # use len(content), not file.size
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": False,
                "message": f"file size should be under {MAX_UPLOAD_SIZE.get(exe, 0)}"
            }
        )

    # compress content
    if compress:
        content = zlib.compress(content)

    buffer = io.BytesIO(content)

    async def stream_base64():
        while True:
            chunk = buffer.read(8192)
            if not chunk:
                break
            yield b64encode(chunk)

    return StreamingResponse(
        stream_base64(),
        media_type="text/plain",
        headers={
            "Content-Disposition": f"inline; filename={file.filename}.b64"
        }
    )
