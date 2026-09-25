"""API contract. Keep in sync with web/src/lib/types.ts."""

from typing import Literal

from pydantic import BaseModel, Field

# en: English, hi-ur: Hindi/Urdu (one spoken language, two scripts),
# ar: Arabic (incl. Arabizi), ne: named entity, other: emoji/numbers/punctuation
Lang = Literal["en", "hi-ur", "ar", "ne", "other"]


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    # "auto" = fallback chain, or one model id from GET /providers (no fallback).
    provider: str = Field(default="auto", max_length=100)


class ProviderOption(BaseModel):
    id: str  # "auto" or a model id, e.g. "gemini-3.5-flash-lite"
    label: str  # e.g. "Gemini 3.5 Flash-Lite"
    vendor: str  # e.g. "Google Gemini", "Groq", or "" for auto


class ProvidersResponse(BaseModel):
    default: str
    options: list[ProviderOption]


class Token(BaseModel):
    text: str
    start: int
    end: int
    lang: Lang
    conf: float = Field(ge=0, le=1)
    key: str | None = None  # sound key: spellings that sound alike share it
    scripts: dict[str, str] = {}  # e.g. {"deva": "भाई", "urdu": "بھائی", "arabic": "بعد"}


class Stats(BaseModel):
    languages: list[Lang]
    switch_points: int
    cmi: float  # Code-Mixing Index (Das & Gambäck 2014), 0 = monolingual


class Meaning(BaseModel):
    """What the LLM must return (also used as its JSON schema)."""

    en: str  # what the message means, in plain English
    reply: str  # a short reply written the way the sender writes (same language mix)


class MeaningResult(Meaning):
    provider: str  # model that answered, e.g. "gemini-3.1-flash-lite"
    register_kept: bool  # our language ID found the reply keeps the sender's language mix


class AnalyzeResponse(BaseModel):
    tokens: list[Token]
    stats: Stats
    meaning: MeaningResult | None = None
    lid_source: Literal["model", "rules"]
