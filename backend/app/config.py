from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    env: str = "development"
    gcp_project: str = "citypulse-dev"
    bq_dataset: str = "civic_dev"
    gemini_model: str = "gemini-2.0-flash"
    gemini_api_key: str = ""
    log_level: str = "DEBUG"
    cors_origins: str = "http://localhost:5173"
    data_dir: str = "../data/datasets"

    class Config:
        env_prefix = "CITYPULSE_"
        env_file = ".env"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string or '*'."""
        raw = self.cors_origins.strip()
        # Handle JSON array format for backward compat
        if raw.startswith("["):
            import json
            try:
                return json.loads(raw)
            except Exception:
                pass
        # Handle wildcard
        if raw == "*":
            return ["*"]
        # Comma-separated
        return [o.strip() for o in raw.split(",") if o.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()

