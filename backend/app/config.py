from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://dbadmin:Password123@localhost:5432/boilerworks"
    redis_url: str = "redis://localhost:6379/1"
    secret_key: str = "change-me-in-production"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]
    session_max_age_days: int = 30

    model_config = {"env_prefix": "APP_"}


settings = Settings()
