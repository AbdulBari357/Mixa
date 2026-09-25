"""Stage 2: word-level language identification.

Uses the trained CRF at ``models/lid.joblib`` when it exists (see ml/train_lid.py).
Until then, and as the baseline we report the model against, it falls back to
simple rules: script detection, Arabizi digits and small seed word lists.
"""

import logging
import re
from functools import lru_cache

import joblib

from mixa.config import get_settings
from mixa.pipeline.features import script_of, sentence_features
from mixa.pipeline.tokenize import RawToken

log = logging.getLogger(__name__)

# Letters that appear in Urdu but not in Arabic.
_URDU_ONLY = set("ٹڈڑںےۓہھ")

# Seed lists for the rules baseline only. The trained model replaces these.
# Words that are also common English words (the, he, me, main, mat, par, late, ya...) are
# deliberately left out: without context they turned plain English into "Hindi".
_HI_UR_SEED = set(
    """
    hai hain ho hoon tha thi kya kyu kyun kaise kahan kab kal aaj abhi nahi nhi nahin
    na haan bhai yaar yar bahut bohot bahot thoda zyada jyada accha acha achha theek thik
    mera meri mere tera teri tere apna apni hum tum aap mai mujhe tujhe usko isko
    aur lekin pe ko ka ki ke se mein tak wala wali wale kuch sab koi
    raha rahi rahe gaya gayi gaye karna karo kar karke jana jao ja aana aao aa dekho bolo
    samajh samaj pata chal chalo matlab bas phir jaldi hoga hogi arre bilkul zaroor sahi
    batao bata dost ghar kaam kitna kaun kidhar idhar udhar yahan wahan kyunki
    """.split()
)
_AR_SEED = set(
    """
    yalla wallah walla habibi habibti inshallah insha'allah mashallah alhamdulillah khalas
    shukran ana inta enta inti enti huwa hiya shu shlonak shlonik zain zein wayed
    wayid mafi akhi ukhti salam salaam marhaba ahlan tamam aywa la2 laa ma3 3ala
    ba3d ba3den 7abibi 3ashan 3shan ta3al yallah khalli maalesh mashi shwaya shwayya
    wainak wain kteer kthir
    """.split()
)
_ARABIZI_DIGITS = set("235679")
# Numbers with units or ordinals (5pm, 2nd, 10k, 30min) are not Arabizi.
_NUMBER_WITH_UNIT = re.compile(
    r"\d+(am|pm|st|nd|rd|th|k|m|h|hr|hrs|min|mins|s|sec|kg|km|gb|mb|x|d)"
)


@lru_cache
def _load_model():
    path = get_settings().models_dir / "lid.joblib"
    if not path.exists():
        return None
    log.info("Loading language-ID model from %s", path)
    return joblib.load(path)


def model_available() -> bool:
    return _load_model() is not None


def _rule_label(tok: RawToken) -> tuple[str, float]:
    if tok.kind != "word":
        return "other", 1.0
    word = tok.text
    script = script_of(word)
    if script == "deva":
        return "hi-ur", 0.99
    if script == "arab":
        return ("hi-ur", 0.9) if any(c in _URDU_ONLY for c in word) else ("ar", 0.8)
    low = word.lower()
    if low in _AR_SEED:
        return "ar", 0.8
    if _NUMBER_WITH_UNIT.fullmatch(low):
        return "other", 0.9
    if any(c in _ARABIZI_DIGITS for c in low) and any(c.isalpha() for c in low):
        return "ar", 0.75
    if low in _HI_UR_SEED:
        return "hi-ur", 0.75
    return "en", 0.5


def identify(tokens: list[RawToken]) -> tuple[list[tuple[str, float]], str]:
    """Label each token. Returns (labels with confidence, source) with source "model" or "rules".

    Hybrid: the CRF labels Latin-script words (where context matters: "main" in "main gate"
    vs "main aa raha hoon"). Devanagari and Arabic/Urdu-script words keep the script rule,
    which is exact there and covers Urdu script, which no training set has.
    """
    crf = _load_model()
    if crf is None:
        return [_rule_label(t) for t in tokens], "rules"

    labels: list[tuple[str, float]] = [("other", 1.0)] * len(tokens)
    word_idx = [i for i, t in enumerate(tokens) if t.kind == "word"]
    if word_idx:
        word_labels = label_words(crf, [tokens[i].text for i in word_idx])
        for i, label in zip(word_idx, word_labels):
            labels[i] = label
    return labels, "model"


def label_words(crf, words: list[str]) -> list[tuple[str, float]]:
    """The model's labels for a sentence's word tokens, with confidences.

    The single decoding path shared by serving (identify) and evaluation (ml/train_lid.py):
    per-word most likely label from the CRF's marginals, and the exact script rule for
    Devanagari / Arabic-script words.
    """
    out = []
    for word, probs in zip(words, crf.predict_marginals_single(sentence_features(words))):
        if script_of(word) in ("deva", "arab"):
            out.append(_rule_label(RawToken(word, 0, len(word), "word")))
        else:
            best = max(probs, key=probs.get)
            out.append((best, round(probs[best], 3)))
    return out
