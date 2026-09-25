# Architecture

## Framing

The problem statement criticises tools that learn "one clean official version" of a
language. So Mixa's rule is **understand without correcting**: `bohot`, `bahut`, `bht`,
`बहुत` and `بہت` are all the same word and none of them is wrong. We extract meaning
and structure, and we keep the user's own words and register.

## System

```
Web app (Next.js)  ──POST /analyze──▶  FastAPI service
                                         │
                                         ├─ 1. Tokenizer          keeps 7abibi / ba3d / भाई whole
                                         ├─ 2. Language ID  ◀──── models/lid.joblib (CRF, trained in api/ml/)
                                         ├─ 3. Sound keys   ◀──┐
                                         ├─ 4. Script views ◀──┴─ variant lexicon (Dakshina + Arabizi rules)
                                         └─ 5. Meaning      ◀──── Gemini API (cached)
```

| Stage | Module | Approach | How we measure it |
|---|---|---|---|
| 1. Tokenize | `pipeline/tokenize.py` | Unicode-category scanner; digits, matras and in-word apostrophes stay inside words | Unit tests |
| 2. Language ID | `pipeline/lid.py`, `pipeline/features.py` | CRF over char n-grams, prefixes/suffixes, script, Arabizi digits, sound key, neighbouring words. Rules fallback = our baseline | Per-label P/R/F1 on LinCE dev, model vs rules |
| 3. Sound keys | `pipeline/soundkey.py` | Consonant skeleton + final-vowel class; Arabizi digits mapped; `h` dropped except word-initially | Grouping precision/recall on Dakshina romanization lexicons |
| 4. Script views | `pipeline/scripts.py` | Dakshina lookup (Hindi/Urdu), rule table (Arabizi -> Arabic), LLM fallback | Spot checks |
| 5. Meaning | `pipeline/meaning.py` | Gemini with the text plus our word tags, structured JSON output | Demo examples |

### Labels

`en`, `hi-ur`, `ar`, `ne` (named entity), `other` (emoji, numbers, punctuation).
Hindi and Urdu share `hi-ur`: romanized, they are the same spoken language and can't
honestly be told apart word by word. Native script tells them apart when present.

### Code-Mixing Index

`CMI = 100 × (1 − max_lang_count / (n − u))` (Das & Gambäck, 2014), where `u` counts
language-independent tokens. 0 means monolingual.

## API contract

Source of truth: `api/src/mixa/schemas.py`, mirrored in `web/src/lib/types.ts`.

```
POST /analyze  {"text": "..."}
  -> {tokens: [{text, start, end, lang, conf, key, scripts}],
      stats: {languages, switch_points, cmi},
      meaning: {en, same_register} | null,
      lid_source: "model" | "rules"}
GET  /health   -> {status, lid_model, gemini}
```

Planned: `POST /search` (sound-aware search over sample messages).

## Web screens

1. **Analyze**: colour-coded word strip, script views, stats, meaning.
2. **Standard tool vs Mixa**: the same message through a normal spell-checker (all red) next to ours.
3. **Search by sound**: `bahut` finds `bohot`, `bht`, `بہت`.

## Decisions

- **Python API runs in Docker.** The dev laptop's Windows Smart App Control blocks
  unsigned native Python binaries and DLLs. A Linux container avoids that and doubles
  as the deployment image.
- **CRF, not a transformer, for language ID.** Trains in minutes on a laptop CPU, is
  explainable to judges, and is a well-established approach for code-switched LID.
- **The LLM is the last stage, not the whole system.** It receives our tags, so its
  output is grounded in what our own model found.

## Deployment

- Web: Vercel.
- API: `api/Dockerfile` (default `prod` target, port 7860) on Hugging Face Spaces.
