from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "sqlite:///./shortener.db"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()
