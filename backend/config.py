"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    lexguard_env: str = "development"
    lexguard_db_url: str = "sqlite:///./lexguard.db"
    lexguard_debug: bool = True
    lexguard_version: str = "0.1.0"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
