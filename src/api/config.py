"""API configuration using pydantic-settings."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    environment: str = "development"

    model_config = {"env_file": ".env", "env_prefix": "API_", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
