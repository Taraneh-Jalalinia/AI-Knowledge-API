from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./knowledge.db"
    redis_url: str = "redis://localhost:6379/0"
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection: str = "knowledge_docs"

    jwt_secret_key: str = "change-me-in-production"
    jwt_refresh_secret_key: str = "change-me-refresh-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 10080

    upload_dir: str = "uploads"
    rag_mock: bool = False
    cache_ttl_seconds: int = 3600


@lru_cache
def get_settings() -> Settings:
    return Settings()
