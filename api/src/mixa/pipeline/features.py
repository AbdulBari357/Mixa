"""Per-token features for the word-level language-ID CRF.

Shared by training (ml/train_lid.py) and inference (pipeline/lid.py) so the two
can never drift apart. Change features here, then retrain.
"""

import re

from mixa.pipeline.soundkey import sound_key

_ARABIZI_DIGITS = set("235679")
_LONG_RUNS = re.compile(r"(.)\1{2,}")


def normalise(word: str) -> str:
    """Lowercase and cut letter runs to 2 (bahuttttt -> bahutt), as the Haifa corpus does."""
    return _LONG_RUNS.sub(r"\1\1", word.lower())


def script_of(word: str) -> str:
    for ch in word:
        cp = ord(ch)
        if 0x0900 <= cp <= 0x097F:
            return "deva"
        if 0x0600 <= cp <= 0x06FF or 0x0750 <= cp <= 0x077F or 0x08A0 <= cp <= 0x08FF:
            return "arab"
        if ch.isascii() and ch.isalpha():
            return "latn"
    return "other"


def _word_features(word: str, prefix: str) -> dict[str, object]:
    low = normalise(word)
    return {
        f"{prefix}lower": low,
        f"{prefix}suf3": low[-3:],
        f"{prefix}script": script_of(word),
        f"{prefix}key": sound_key(word) or "",
    }


def token_features(words: list[str], i: int) -> dict[str, object]:
    word = words[i]
    low = normalise(word)
    padded = f"<{low}>"
    has_letter = any(c.isalpha() for c in low)
    feats: dict[str, object] = {
        "bias": 1.0,
        "is_title": word.istitle(),
        "is_upper": word.isupper() and len(word) > 1,
        "len": min(len(word), 10),
        "has_arabizi_digit": has_letter and any(c in _ARABIZI_DIGITS for c in low),
        "pre1": low[:1],
        "pre2": low[:2],
        "pre3": low[:3],
        "suf1": low[-1:],
        "suf2": low[-2:],
        **_word_features(word, ""),
    }
    for n in (2, 3, 4):
        for k in range(len(padded) - n + 1):
            feats[f"ng{n}={padded[k : k + n]}"] = 1.0
    if i > 0:
        feats.update(_word_features(words[i - 1], "-1:"))
    else:
        feats["BOS"] = True
    if i < len(words) - 1:
        feats.update(_word_features(words[i + 1], "+1:"))
    else:
        feats["EOS"] = True
    return feats


def sentence_features(words: list[str]) -> list[dict[str, object]]:
    return [token_features(words, i) for i in range(len(words))]
