from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "AI Product Search Platform"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    database_url: str
    database_echo: bool = False
    database_pool_size: int = 20
    database_max_overflow: int = 10
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    jwt_refresh_expiration_days: int = 7
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"
    openai_timeout: int = 30
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    wildberries_api_key: str = ""
    ozon_api_key: str = ""
    avito_api_key: str = ""
    free_plan_daily_searches: int = 10
    pro_plan_daily_searches: int = 1000

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
