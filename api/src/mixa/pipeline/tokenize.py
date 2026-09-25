"""Stage 1: split text into word and non-word tokens, keeping character offsets.

Unlike a typical tokenizer this keeps Arabizi words such as ``7abibi`` and ``ba3d``
whole (digits are part of the word), keeps Devanagari/Urdu vowel signs attached to
their letters, and keeps in-word apostrophes (``I'll``, ``ba'd``).
"""

import unicodedata
from dataclasses import dataclass
from typing import Literal

_APOSTROPHES = "'’"
_JOINERS = "‌‍"  # ZWNJ / ZWJ, used inside Urdu and Hindi words


@dataclass(frozen=True)
class RawToken:
    text: str
    start: int
    end: int
    kind: Literal["word", "number", "symbol"]


def _is_word_char(ch: str) -> bool:
    # Letters, digits and combining marks (matras, harakat) all belong to a word.
    return unicodedata.category(ch)[0] in "LNM"


def _continues_word(text: str, j: int) -> bool:
    c = text[j]
    if _is_word_char(c) or c in _JOINERS:
        return True
    # In-word apostrophe: I'll, ba'd
    return c in _APOSTROPHES and j + 1 < len(text) and _is_word_char(text[j + 1])


def tokenize(text: str) -> list[RawToken]:
    tokens: list[RawToken] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        j = i + 1
        if _is_word_char(ch):
            while j < n and _continues_word(text, j):
                j += 1
            word = text[i:j]
            kind = "number" if word.isdigit() else "word"
        else:
            # Group runs of punctuation / emoji ("?!", "😂😂") into one token.
            while j < n and not text[j].isspace() and not _is_word_char(text[j]):
                j += 1
            kind = "symbol"
        tokens.append(RawToken(text[i:j], i, j, kind))
        i = j
    return tokens
