from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URI: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/shortener"
    )
    DATABASE_ENGINE_POOL_TIMEOUT: int = 30
    DATABASE_ENGINE_POOL_RECYCLE: int = 3600
    DATABASE_ENGINE_POOL_SIZE: int = 10
    DATABASE_ENGINE_MAX_OVERFLOW: int = 20
    DATABASE_ENGINE_POOL_PING: bool = True
    DEFAULT_DOMAIN: str = "http://localhost:8000"
    SHORT_URL_LENGTH: int = 6

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
