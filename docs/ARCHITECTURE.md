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
                                         └─ 5. Meaning      ◀──── LLM chain: Gemini 3.5 Flash-Lite
                                                                   → Groq GPT-OSS 120B → Gemini 3.1 Flash-Lite
                                                                   (reply checked by our LID, SQLite-cached)
```

| Stage | Module | Approach | How we measure it |
|---|---|---|---|
| 1. Tokenize | `pipeline/tokenize.py` | Unicode-category scanner; digits, matras and in-word apostrophes stay inside words | Unit tests |
| 2. Language ID | `pipeline/lid.py`, `pipeline/features.py` | CRF over char n-grams, prefixes/suffixes, script, Arabizi digits, sound key, neighbouring words. Rules fallback = our baseline | Per-label P/R/F1 on LinCE dev, model vs rules |
| 3. Sound keys | `pipeline/soundkey.py` | Consonant skeleton + final-vowel class; Arabizi digits mapped; `h` dropped except word-initially | Grouping precision/recall on Dakshina romanization lexicons |
| 4. Script views | `pipeline/scripts.py` | Dakshina lookup (Hindi/Urdu), rule table (Arabizi -> Arabic), LLM fallback | Spot checks |
| 5. Meaning | `pipeline/meaning.py`, `pipeline/llm.py` | LLM gets the text plus our word tags and returns JSON `{en, reply}`. Our own LID checks the reply kept the sender's language; if not (or it echoed / was empty) the next model in the chain is tried | `ml/eval_meaning.py` → [`meaning_eval.md`](../api/ml/results/meaning_eval.md): 5 models × 13 messages |

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
POST /analyze    {"text": "... (max 500 chars)", "provider": "auto" | <model id>}
  -> {tokens: [{text, start, end, lang, conf, key, scripts}],
      stats: {languages, switch_points, cmi},
      meaning: {en, reply, provider, register_kept} | null,
      lid_source: "model" | "rules"}
GET  /providers  -> {default: "auto", options: [{id, label, vendor}]}   (only models with a key)
GET  /health     -> {status, lid_model, meaning_providers, recent_failures}
```

Planned: `POST /search` (sound-aware search over sample messages).

## Web screens

1. **Analyze**: colour-coded word strip, script views, stats, meaning and a reply in the
   sender's own mix. A **Model** dropdown picks "Auto" (the fallback chain) or one specific
   LLM, so anyone can compare how each model handles code-mixing.
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
- **Our model grades the LLM.** LLMs often "defect" to plain English when asked to answer
  in a code-mixed register (reported for Gemini, GPT and Claude in the Indi-RomCoM
  benchmark, 2026). Every reply is re-tagged by our language ID; a reply that dropped the
  sender's languages falls through to the next model.
- **Instructions in the system prompt, the message in the user turn.** With one combined
  user message, GPT-OSS 120B answered the instructions themselves ("Got it, will follow the
  guidelines!") on 5 of 13 test messages; after the split it answered 13/13
  (`ml/results/meaning_eval_v2_single_prompt.md` vs `meaning_eval_v3_system_prompt.md`).
- **Chain order from measurements.** Gemini 3.5 Flash-Lite had the best Arabizi replies at
  ~1 s; GPT-OSS 120B (a different vendor, so one outage can't take out both) is second;
  Gemini 3.1 Flash-Lite (~3 s, occasional 503s) is last.
- **Free tiers only, with guard rails.** 20 LLM calls/minute across the API, 10 s per call
  (Gemini's minimum deadline), 15 s per request, successful answers cached. Free tiers may use prompts for training, so
  the UI says so and the eval uses synthetic messages only.
- **The LLM stage can never break the rest.** Any failure there (quota, network, cache disk)
  returns `meaning: null`; tokens and stats are still returned.

## Deployment

- Web: Vercel.
- API: `api/Dockerfile` (default `prod` target, port 7860) on Hugging Face Spaces. The
  prod image writes its cache to `/tmp` (Spaces run as uid 1000). Keys go in the Space's
  Secrets, never in files. List settings must be JSON, e.g.
  `ALLOWED_ORIGINS=["https://<app>.vercel.app"]`.
