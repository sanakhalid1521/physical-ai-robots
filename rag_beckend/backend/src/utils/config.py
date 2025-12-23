from pydantic_settings import BaseSettings
from typing import Optional
import os
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Qdrant Configuration
    qdrant_url: str = os.getenv("QDRANT_URL", "")
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")

    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "")

    # Application Configuration
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "info")

    # API Configuration
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()


# Convenience functions to access individual settings
def get_openai_api_key() -> str:
    return get_settings().openai_api_key


def get_qdrant_url() -> str:
    return get_settings().qdrant_url


def get_qdrant_api_key() -> str:
    return get_settings().qdrant_api_key


def get_database_url() -> str:
    return get_settings().database_url


def get_app_env() -> str:
    return get_settings().app_env


def get_log_level() -> str:
    return get_settings().log_level