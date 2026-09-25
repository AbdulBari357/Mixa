from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = ""
    gemini_model: str = "gemini-flash-latest"
    allowed_origins: list[str] = ["http://localhost:3000"]
    models_dir: Path = Path(__file__).resolve().parents[2] / "models"


@lru_cache
def get_settings() -> Settings:
    return Settings()
