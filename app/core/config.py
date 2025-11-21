from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    target_url: str = "https://ai.megallm.io"
    host: str = "0.0.0.0"
    port: int = 8080
    request_timeout: int = 300
    log_level: str = "INFO"
    max_workers: int = 4
    enable_cors: bool = True
    cors_origins: list = ["*"]
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    proxy_buffer_size: int = 8192
    max_retries: int = 3
    retry_backoff_factor: float = 0.5
    ssl_verify: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
