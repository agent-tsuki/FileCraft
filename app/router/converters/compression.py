from fastapi import UploadFile, Query, APIRouter, status
from fastapi.responses import StreamingResponse, JSONResponse
from PIL import Image, UnidentifiedImageError
import zlib
import io
import os

router = APIRouter()
CHUNK_SIZE = 8192
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "tiff", "bmp", "gif"}

@router.post("/smart-compress")
async def smart_compress_file(
    file: UploadFile,
    compression_level: int = Query(default=6, ge=1, le=9),
    quality: int = Query(default=70, ge=10, le=95, description="Image quality (JPEG/WebP)"),
    force_webp: bool = Query(default=False, description="Convert all images to WebP"),
):
    if not file.filename:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": False, "message": "Missing file"}
        )

    filename, ext = os.path.splitext(file.filename)
    ext = ext.lower().strip(".")

    content = await file.read()

    if ext in IMAGE_EXTENSIONS:
        try:
            input_buffer = io.BytesIO(content)
            image = Image.open(input_buffer)

            # ✅ Strip all metadata
            data = list(image.getdata())
            image_no_meta = Image.new(image.mode, image.size)
            image_no_meta.putdata(data)

            # ✅ Convert to RGB if needed (JPEG can't handle RGBA)
            if image_no_meta.mode in ("RGBA", "P"):
                image_no_meta = image_no_meta.convert("RGB")

            output = io.BytesIO()

            # ✅ Choose output format
            target_format = "WEBP" if force_webp else image.format or "JPEG"
            target_ext = "webp" if force_webp else (ext if ext != "jpg" else "jpeg")

            save_kwargs = {
                "optimize": True,
                "quality": quality
            }

            if target_format.upper() == "PNG":
                save_kwargs["compress_level"] = 9

            image_no_meta.save(output, format=target_format, **save_kwargs)
            output.seek(0)

            return StreamingResponse(
                output,
                media_type=f"image/{target_ext}",
                headers={
                    "Content-Disposition": f"inline; filename={filename}_compressed.{target_ext}"
                }
            )

        except UnidentifiedImageError:
            return JSONResponse(
                status_code=400,
                content={"status": False, "message": "Invalid image format"}
            )

    else:
        # Binary file compression fallback
        buffer = io.BytesIO(content)

        def stream_zlib():
            compressor = zlib.compressobj(compression_level)
            while chunk := buffer.read(CHUNK_SIZE):
                yield compressor.compress(chunk)
            yield compressor.flush()

        return StreamingResponse(
            stream_zlib(),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.wxct"
            }
        )
