"""Stage 3: reduce a romanized word to a "sound key" so spellings by ear group together.

    bahut, bohot, bahot, bht, bahuttt  -> "bt"
    hai, he, hy, hay                   -> "hE"
    samajh, samaj, samjh               -> "smj"
    7abibi, habibi                     -> "hbI"

The key keeps the consonant skeleton (vowels in the middle are what people vary
most when spelling by ear) plus a coarse class for the final vowel, which carries
meaning in short words (hai vs ho). "h" is dropped except at the start of a word:
it is spelled inconsistently both as aspiration (samajh/samaj, bhai/bai) and as a
vowel-ish sound (bahut/baut/bht). Tune the rules against the Dakshina
romanization lexicon: every romanization of one native word should share a key.
"""

import re

# Arabizi digits stand in for Arabic letters with no Latin equivalent.
_ARABIZI_DIGITS = str.maketrans(
    {"2": "", "3": "", "5": "kh", "6": "t", "7": "h", "8": "gh", "9": "q"}
)
_SUBSTITUTIONS = [
    (re.compile(r"ph"), "f"),
    (re.compile(r"ck"), "k"),
    (re.compile(r"q"), "k"),
    (re.compile(r"c(?!h)"), "k"),
    (re.compile(r"w"), "v"),
    (re.compile(r"z"), "j"),
    (re.compile(r"x"), "ks"),
    # A final h after a vowel is usually silent: yeh/ye, woh/wo, nah/na.
    (re.compile(r"([aeiouy])h$"), r"\1"),
]
_REPEATS = re.compile(r"(.)\1+")
_VOWELS = "aeiouy"


def _final_vowel_class(tail: str) -> str:
    if not tail:
        return ""
    if tail.endswith("ai") or tail[-1] in "ey":
        return "E"
    if tail[-1] in "ou":
        return "O"
    if tail[-1] == "i":
        return "I"
    return "A"


def sound_key(word: str) -> str | None:
    """Return the sound key for a Latin-script word, or None if it has no Latin letters."""
    w = word.lower()
    if any(c.isdigit() for c in w) and any(c.isalpha() for c in w):
        w = w.translate(_ARABIZI_DIGITS)
    w = re.sub(r"[^a-z]", "", w)
    if not w:
        return None
    w = _REPEATS.sub(r"\1", w)
    for pattern, repl in _SUBSTITUTIONS:
        w = pattern.sub(repl, w)

    stem = w.rstrip(_VOWELS)
    tail = w[len(stem) :]
    if not stem:  # all vowels: "a", "ai", "yaa"
        return "_" + _final_vowel_class(tail)
    skeleton = stem[0] + re.sub(f"[{_VOWELS}h]", "", stem[1:])
    return _REPEATS.sub(r"\1", skeleton) + _final_vowel_class(tail)
