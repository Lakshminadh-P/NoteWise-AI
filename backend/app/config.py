from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database (defaults to local sqlite for zero-config run, override with Postgres via env)
    DATABASE_URL: str = "sqlite+aiosqlite:///./notewise.db"

    # JWT
    JWT_SECRET_KEY: str = "change-me-to-a-long-random-string"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI
    GEMINI_API_KEY: str = ""

    # Storage
    UPLOAD_DIR: str = "./uploads"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
