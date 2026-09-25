"""LLM providers for the meaning stage. Each turns (system, user) prompts into a ``Meaning``.

Instructions go in the system prompt and only the message in the user turn: with a
single combined user message, gpt-oss replied to the instructions themselves
("Got it, will follow the guidelines!") on 5 of 13 test messages.

Providers raise on any failure (HTTP error, rate limit, invalid JSON) so the caller
can fall through to the next one in the chain.
"""

import httpx
from google import genai
from google.genai import types

from mixa.schemas import Meaning

MEANING_SCHEMA = {**Meaning.model_json_schema(), "additionalProperties": False}

# Per-model request options for Groq, found by testing each model on 2026-09-25.
_GROQ_OPTIONS: dict[str, dict[str, object]] = {
    # Reasoning models: reasoning tokens count against the free token-per-day budget.
    "openai/gpt-oss-120b": {"reasoning_effort": "low", "max_completion_tokens": 800},
    "openai/gpt-oss-20b": {"reasoning_effort": "low", "max_completion_tokens": 800},
    # Free tier caps this model at 1,000 output tokens per minute.
    "qwen/qwen3.8-27b": {"reasoning_effort": "none", "max_completion_tokens": 400},
}
# Models that reject strict json_schema and only support JSON mode.
_GROQ_JSON_MODE_ONLY = {"allam-2-7b"}
# The SDK forwards the timeout to Google as a server deadline, and Google rejects any
# deadline under 10 s with 400 INVALID_ARGUMENT (found when an 8 s timeout silently
# failed every Gemini call and the chain fell through to Groq).
GEMINI_MIN_TIMEOUT_S = 10.0


def gemini_timeout_ms(timeout_s: float) -> int:
    return int(max(timeout_s, GEMINI_MIN_TIMEOUT_S) * 1000)


class GeminiProvider:
    def __init__(self, model: str, api_key: str, timeout_s: float) -> None:
        self.name = model
        self._client = genai.Client(
            api_key=api_key, http_options=types.HttpOptions(timeout=gemini_timeout_ms(timeout_s))
        )

    def generate(self, system: str, user: str) -> Meaning:
        # No temperature: Google recommends the default for Gemini 3 models.
        config = types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json",
            response_json_schema=MEANING_SCHEMA,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        resp = self._client.models.generate_content(model=self.name, contents=user, config=config)
        return Meaning.model_validate_json(resp.text or "")


class GroqProvider:
    def __init__(self, model: str, api_key: str, timeout_s: float) -> None:
        self.name = model
        self._http = httpx.Client(
            base_url="https://api.groq.com/openai/v1",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout_s,
        )
        if model in _GROQ_JSON_MODE_ONLY:
            response_format: dict[str, object] = {"type": "json_object"}
        else:
            response_format = {
                "type": "json_schema",
                "json_schema": {"name": "meaning", "strict": True, "schema": MEANING_SCHEMA},
            }
        self._body = {"model": model, "response_format": response_format}
        self._body.update(_GROQ_OPTIONS.get(model, {}))

    def generate(self, system: str, user: str) -> Meaning:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        body = {**self._body, "messages": messages}
        resp = self._http.post("/chat/completions", json=body)
        resp.raise_for_status()
        return Meaning.model_validate_json(resp.json()["choices"][0]["message"]["content"])


def build_provider(spec: str, gemini_key: str, groq_key: str, timeout_s: float):
    """Build a provider from "<provider>:<model>", or None if its API key is missing."""
    kind, _, model = spec.partition(":")
    if kind == "gemini" and gemini_key:
        return GeminiProvider(model, gemini_key, timeout_s)
    if kind == "groq" and groq_key:
        return GroqProvider(model, groq_key, timeout_s)
    if kind not in ("gemini", "groq"):
        raise ValueError(f"Unknown LLM provider in meaning_chain: {spec!r}")
    return None
