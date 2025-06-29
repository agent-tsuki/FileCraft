from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings

from app.router.converters import base64
from app.router.converters import images
from app.router.converters import compression

app = FastAPI(
    title="FileCraft",
    description="FastAPI project for file conversion.",
    version="1.0.0",
    debug=settings.DEBUG,
    docs_url=settings.DOCS,
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all router here
app.include_router(base64.base64Router, tags=["Converter"])
app.include_router(images.imageRouter, tags=["Converter"])
app.include_router(compression.router, tags=["Converter "])


@app.get("/system-check")
def system_check():
    return {
        "status": True,
        "message": "File Craft is up",
    }
