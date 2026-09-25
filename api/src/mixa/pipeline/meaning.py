"""Stage 5: meaning. Gemini reads the text *and* our word-level tags.

Returns None when no API key is configured or the call fails, so the rest of the
pipeline always works offline.
"""

import json
import logging
from functools import lru_cache

from google import genai
from google.genai import types

from mixa.config import get_settings
from mixa.schemas import Meaning

log = logging.getLogger(__name__)

_PROMPT = """You are reading a message from someone who mixes languages, spells words by ear,
and may write one language in another language's script. Their way of writing is not a mistake.

Message: {text}

Word-level language tags from our model (en = English, hi-ur = Hindi/Urdu, ar = Arabic/Arabizi):
{tags}

Return JSON with:
- "en": what the message means, in plain English.
- "same_register": the same meaning re-said naturally in the writer's own mix of languages and
  spelling style. Do not standardise or "correct" it."""


@lru_cache
def _client() -> genai.Client | None:
    key = get_settings().gemini_api_key
    return genai.Client(api_key=key) if key else None


# Successful answers only, so a transient failure is retried next time.
# TODO: move to SQLite so the cache survives restarts during the demo.
_cache: dict[tuple[str, str], Meaning] = {}


def explain(text: str, tags_json: str) -> Meaning | None:
    if (text, tags_json) in _cache:
        return _cache[text, tags_json]
    client = _client()
    if client is None:
        return None
    tags = "\n".join(f"{w} -> {lang}" for w, lang in json.loads(tags_json))
    try:
        resp = client.models.generate_content(
            model=get_settings().gemini_model,
            contents=_PROMPT.format(text=text, tags=tags),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Meaning,
                temperature=0.3,
            ),
        )
        result = (
            resp.parsed
            if isinstance(resp.parsed, Meaning)
            else Meaning.model_validate_json(resp.text)
        )
    except Exception:
        log.exception("Gemini call failed")
        return None
    _cache[text, tags_json] = result
    return result
