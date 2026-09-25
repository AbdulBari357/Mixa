"""API contract. Keep in sync with web/src/lib/types.ts."""

from typing import Literal

from pydantic import BaseModel, Field

# en: English, hi-ur: Hindi/Urdu (one spoken language, two scripts),
# ar: Arabic (incl. Arabizi), ne: named entity, other: emoji/numbers/punctuation
Lang = Literal["en", "hi-ur", "ar", "ne", "other"]


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


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
    en: str
    same_register: str  # the same message, re-said in the user's own mix of languages


class AnalyzeResponse(BaseModel):
    tokens: list[Token]
    stats: Stats
    meaning: Meaning | None = None
    lid_source: Literal["model", "rules"]
