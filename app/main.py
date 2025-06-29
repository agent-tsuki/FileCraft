from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings


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


@app.get("/system-check")
def system_check():
    return {
        "status": True,
        "message": "File Craft is up",
    }
