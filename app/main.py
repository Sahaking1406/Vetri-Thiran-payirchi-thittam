from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routes import router


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent.parent
)

STATIC_DIR = (
    BASE_DIR / "static"
)


app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-powered personalized "
        "comic story creator."
    ),
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(
        directory=STATIC_DIR
    ),
    name="static",
)


app.include_router(
    router
)


@app.get(
    "/health",
    tags=["system"],
)
def health():

    return {
        "status": "ok",
        "app": settings.app_name,
        "image_provider": (
            settings.image_provider
        ),
        "gemini_configured": bool(
            settings.gemini_api_key
        ),
        "huggingface_configured": bool(
            settings.hf_token
        ),
    }