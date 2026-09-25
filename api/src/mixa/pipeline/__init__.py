"""The analysis pipeline: tokenize -> language ID -> sound keys -> script views -> meaning."""

import logging
from itertools import pairwise

from mixa.pipeline.lid import identify
from mixa.pipeline.meaning import AUTO, explain
from mixa.pipeline.scripts import script_views
from mixa.pipeline.soundkey import sound_key
from mixa.pipeline.tokenize import tokenize
from mixa.schemas import AnalyzeResponse, Stats, Token

_LANGUAGE_INDEPENDENT = {"other", "ne"}

log = logging.getLogger(__name__)


def compute_stats(langs: list[str]) -> Stats:
    tagged = [lang for lang in langs if lang not in _LANGUAGE_INDEPENDENT]
    seen = list(dict.fromkeys(tagged))
    switches = sum(1 for a, b in pairwise(tagged) if a != b)
    # Code-Mixing Index (Das & Gambäck, 2014): 100 * (1 - max_i(w_i) / (n - u))
    cmi = 100 * (1 - max(tagged.count(lang) for lang in seen) / len(tagged)) if tagged else 0.0
    return Stats(languages=seen, switch_points=switches, cmi=round(cmi, 1))


def analyze(text: str, with_meaning: bool = True, provider: str = AUTO) -> AnalyzeResponse:
    raw = tokenize(text)
    labels, source = identify(raw)
    tokens = [
        Token(
            text=t.text,
            start=t.start,
            end=t.end,
            lang=lang,
            conf=conf,
            key=sound_key(t.text) if t.kind == "word" else None,
            scripts=script_views(t.text, lang) if t.kind == "word" else {},
        )
        for t, (lang, conf) in zip(raw, labels)
    ]
    meaning = None
    if with_meaning:
        tags = [(t.text, t.lang) for t in tokens if t.lang not in _LANGUAGE_INDEPENDENT]
        try:
            meaning = explain(text, tags, provider)
        except Exception as e:  # noqa: BLE001 - the LLM stage must never take the LID output down
            log.warning("Meaning stage failed: %s", type(e).__name__)
    return AnalyzeResponse(
        tokens=tokens,
        stats=compute_stats([t.lang for t in tokens]),
        meaning=meaning,
        lid_source=source,
    )
