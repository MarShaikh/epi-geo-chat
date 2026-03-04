"""FastAPI application factory."""

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.config import get_settings
from src.api.routes import artifacts, chat, health, stac, tiles


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Epi-Geo Chat API",
        version="0.1.0",
        description="AI-powered geospatial climate data query API",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
    app.include_router(stac.router, prefix="/api/v1", tags=["stac"])
    app.include_router(tiles.router, prefix="/api/v1", tags=["tiles"])
    app.include_router(artifacts.router, prefix="/api/v1", tags=["artifacts"])

    return app


app = create_app()
