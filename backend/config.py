from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash-lite"
    question_count: int = 5
    cache_ttl_seconds: int = 3600
    cors_origins: str = "*"
    jwt_secret_key: str = "dev-secret-change-in-production"
    jwt_expire_hours: int = 72
    database_path: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
