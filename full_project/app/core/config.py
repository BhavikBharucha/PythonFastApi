from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "Production FastAPI Project"
    app_version: str = "1.0.0"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./app.db"

    # JWT
    secret_key: str = "changeme-use-a-real-secret-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    upload_dir: str = "uploads/products"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Login security
    login_max_attempts: int
    login_block_duration_hours: int

    class Config:
        env_file = ".env"


settings = Settings()
