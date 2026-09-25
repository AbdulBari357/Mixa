"""Stage 4: show a word in the scripts its language is normally written in.

Current state: words already in a native script are passed through.
Next: Dakshina lexicon lookup for romanized Hindi/Urdu (-> Devanagari, Urdu),
rule table for Arabizi (-> Arabic), and an LLM fallback for unknown words.
"""

from mixa.pipeline.features import script_of


def script_views(word: str, lang: str) -> dict[str, str]:
    script = script_of(word)
    if script == "deva":
        return {"deva": word}
    if script == "arab":
        return {"urdu": word} if lang == "hi-ur" else {"arabic": word}
    return {}
