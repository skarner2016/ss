from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "community"
    debug: bool = True
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/community"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    resend_api_key: str = ""
    resend_from_email: str = "onboarding@resend.dev"
    code_ttl: int = 600  # 10 minutes
    code_length: int = 6

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
