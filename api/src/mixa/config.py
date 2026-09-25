from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_API_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = ""
    groq_api_key: str = ""
    # Meaning-stage fallback chain, tried in order: "<provider>:<model>". Order chosen from
    # ml/results/meaning_eval.md; a different vendor comes second so one outage can't
    # take out both. Providers without an API key are skipped.
    meaning_chain: list[str] = [
        "gemini:gemini-3.5-flash-lite",
        "groq:openai/gpt-oss-120b",
        "gemini:gemini-3.1-flash-lite",
    ]
    # Extra models the web app can pick explicitly (not part of the automatic chain).
    meaning_extra_models: list[str] = ["groq:openai/gpt-oss-20b", "groq:qwen/qwen3.8-27b"]
    llm_timeout_s: float = 10.0  # per provider call; Gemini rejects anything under 10 s
    llm_chain_budget_s: float = 15.0  # stop trying further providers after this
    llm_calls_per_minute: int = 20  # across all providers; free tiers allow 15 RPM per model
    # Env values for list fields must be JSON, e.g. ALLOWED_ORIGINS=["https://x.vercel.app"]
    allowed_origins: list[str] = ["http://localhost:3000"]
    models_dir: Path = _API_ROOT / "models"
    cache_path: Path = _API_ROOT / ".cache" / "meaning.sqlite"


@lru_cache
def get_settings() -> Settings:
    return Settings()
