from fastapi import APIRouter, Form, UploadFile, status
from fastapi.responses import StreamingResponse, JSONResponse

import io
from PIL import Image

imageRouter = APIRouter(prefix="/images")


@imageRouter.post("/img-converter")
async def image_converter(
    image: UploadFile,
    img_type: str = Form(..., description="e.g. png, jpeg, webp")
):
    try:
        # Read uploaded image into memory
        contents = await image.read()
        input_buffer = io.BytesIO(contents)

        # Open image with PIL
        img = Image.open(input_buffer)

        # Create output buffer
        output_buffer = io.BytesIO()
        img.save(output_buffer, format=img_type.upper())
        output_buffer.seek(0)

        # Determine correct content type
        content_type = (
            f"image/{img_type.lower()}" if img_type.lower() != "jpg" else "image/jpeg"
        )

        return StreamingResponse(
            output_buffer,
            media_type=content_type,
            headers={
                "Content-Disposition": f"inline; filename=converted.{img_type.lower()}"
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": False,
                "message": f"Failed to convert image: {str(e)}"
            }
        )

