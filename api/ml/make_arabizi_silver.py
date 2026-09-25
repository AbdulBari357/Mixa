"""Generate "silver" (LLM-labelled) Arabizi code-switching sentences for training.

No public dataset has word-level language labels for Arabizi mixed with English
(let alone with Hinglish), which is how people in the UAE write. So we ask Gemini
for casual chat sentences with a label on every word, then keep only sentences that
  - re-tokenize with our own tokenizer into exactly the words that were labelled,
  - use only our labels (en / ar / hi-ur / ne),
  - don't contain a UAE test sentence, share a 4-word phrase with one, or overlap one
    heavily (word-set Jaccard >= 0.5).
The generator never sees the test sentences. (A first version listed them in the prompt as
"reserved"; the model then wrote paraphrases of them. An audit caught it; this is the fix.)
Labels are LLM-made, so this is silver data: we never report accuracy on it.

    docker compose run --rm api python ml/make_arabizi_silver.py [n_calls]

Writes ml/silver/arabizi_silver.tsv (committed, so training is reproducible).
"""

import json
import random
import sys
import time
from pathlib import Path

from google import genai
from google.genai import types

from mixa.config import get_settings
from mixa.pipeline.tokenize import tokenize

ML_DIR = Path(__file__).parent
OUT = ML_DIR / "silver" / "arabizi_silver.tsv"
TEST = ML_DIR / "testsets" / "uae_lid.tsv"
MODEL = "gemini-3.5-flash-lite"
PAUSE_S = 4.5  # free tier: 15 requests/minute
SEED = 7

# Gulf is weighted up: no public labelled data has Gulf Arabizi spellings.
DIALECTS = [
    ("Emirati", 3),
    ("Kuwaiti / Qatari / Saudi Gulf", 2),
    ("Levantine (Lebanese/Syrian/Jordanian)", 1),
    ("Egyptian", 1),
]
TOPICS = [
    "traffic and commuting in Dubai/Abu Dhabi",
    "university classes and exams",
    "office work and meetings",
    "ordering food and restaurants",
    "weekend plans and malls",
    "family and relatives",
    "football and sports",
    "shopping and deliveries",
    "Ramadan and Eid",
    "gym and health",
    "phones, apps and gaming",
    "weather and summer heat",
    "travel and airports",
    "friends joking around",
]
MIXES = [
    ("Arabizi mixed with English", 0.7),
    (
        "Arabizi, English AND romanized Hindi/Urdu together (friends from different backgrounds in the UAE)",
        0.3,
    ),
]

SCHEMA = {
    "type": "object",
    "properties": {
        "sentences": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "words": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "w": {"type": "string"},
                                "l": {"type": "string", "enum": ["en", "ar", "hi-ur", "ne"]},
                            },
                            "required": ["w", "l"],
                        },
                    }
                },
                "required": ["words"],
            },
        }
    },
    "required": ["sentences"],
}

PROMPT = """Write {n} different casual chat messages (WhatsApp style) in {mix}.
Dialect: {dialect}. Topic: {topic}.
Rules:
- Arabic words are written in Latin letters (Arabizi), using digits for Arabic sounds where
  people do: 3 = ع, 7 = ح, 2 = ء, 5 = خ, 9 = ص, 6 = ط, 8 = ق, 3' = غ, 9' = ض, 6' = ظ.
  Gulf writers also use ch for ك and g for ق. Vary spellings the way real people do
  (e.g. inshallah / inshalla / insha2allah, ya3ni / yaani, 7abibi / habibi, 6ayeb / tayeb).
- Use real {dialect} words, not Modern Standard Arabic.
- Messages are 4 to 18 words long; mix short and long, English-heavy and Arabizi-heavy.
- Label EVERY word: "ar" = Arabic (Arabizi), "en" = English, "hi-ur" = Hindi/Urdu written in
  Latin letters, "ne" = a name of a person, place, brand or organisation.
- Label by meaning in context, not spelling: e.g. "ana" (Arabic "I") is ar.
- Words only: no punctuation, emoji or standalone numbers in the word list."""


def load_test_sentences() -> list[list[str]]:
    sents, cur = [], []
    for line in TEST.read_text(encoding="utf-8").splitlines() + [""]:
        if line.startswith("#"):
            continue
        if not line.strip():
            if cur:
                sents.append(cur)
            cur = []
        else:
            cur.append(line.split("\t")[0].lower())
    return sents


def _ngrams(words: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def too_close_to_test(words: list[str], tests: list[list[str]]) -> bool:
    """Contains a test sentence, shares a 4-word phrase with one, or Jaccard >= 0.5."""
    low = [w.lower() for w in words]
    joined, grams, bag = f" {' '.join(low)} ", _ngrams(low, 4), set(low)
    for test in tests:
        if f" {' '.join(test)} " in joined or grams & _ngrams(test, 4):
            return True
        if len(bag & set(test)) / len(bag | set(test)) >= 0.5:
            return True
    return False


def valid(words: list[str]) -> bool:
    tokens = tokenize(" ".join(words))
    return [t.text for t in tokens] == words and all(t.kind == "word" for t in tokens)


def main() -> None:
    n_calls = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    client = genai.Client(api_key=get_settings().gemini_api_key)
    rng = random.Random(SEED)
    tests = load_test_sentences()  # used only to FILTER the output, never shown to the LLM
    kept, seen, rejected = [], set(), 0
    for i in range(n_calls):
        mix = rng.choices([m for m, _ in MIXES], [w for _, w in MIXES])[0]
        dialect = rng.choices([d for d, _ in DIALECTS], [w for _, w in DIALECTS])[0]
        prompt = PROMPT.format(n=20, mix=mix, dialect=dialect, topic=rng.choice(TOPICS))
        try:
            resp = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=SCHEMA,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                ),
            )
            batch = json.loads(resp.text)["sentences"]
        except Exception as e:  # noqa: BLE001 - skip a failed call, keep going
            print(f"call {i + 1}: failed ({type(e).__name__})")
            time.sleep(PAUSE_S)
            continue
        for s in batch:
            words = [x["w"].strip() for x in s["words"]]
            labels = [x["l"] for x in s["words"]]
            key = " ".join(words).lower()
            if key in seen or not valid(words) or too_close_to_test(words, tests):
                rejected += 1
                continue
            seen.add(key)
            kept.append((mix.split(" ")[0], words, labels))
        print(f"call {i + 1}/{n_calls}: kept {len(kept)} sentences, rejected {rejected}")
        time.sleep(PAUSE_S)

    OUT.parent.mkdir(exist_ok=True)
    lines = []
    for _, words, labels in kept:
        lines += [f"{w}\t{label}" for w, label in zip(words, labels)] + [""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {len(kept)} sentences to {OUT} (rejected {rejected})")


if __name__ == "__main__":
    main()
