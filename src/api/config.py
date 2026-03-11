"""API configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    environment: str = "development"

    model_config = {"env_file": ".env", "env_prefix": "API_", "extra": "ignore"}

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
