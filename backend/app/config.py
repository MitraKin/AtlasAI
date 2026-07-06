from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    env: str = "development"
    gcp_project: str = "citypulse-dev"
    bq_dataset: str = "civic_dev"
    gemini_model: str = "gemini-2.0-flash"
    gemini_api_key: str = ""
    log_level: str = "DEBUG"
    cors_origins: list[str] = ["http://localhost:5173"]
    data_dir: str = "../data/datasets"

    class Config:
        env_prefix = "CITYPULSE_"
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
