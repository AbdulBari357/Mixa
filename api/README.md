# Mixa API

FastAPI service running the analysis pipeline. See the root README for setup and
`docs/ARCHITECTURE.md` for how the stages fit together.

```
src/mixa/
  server.py            FastAPI app: GET /health, GET /providers, POST /analyze
  schemas.py           API contract (mirrored in web/src/lib/types.ts)
  pipeline/
    tokenize.py        1. tokens with offsets; keeps 7abibi / ba3d / भाई whole
    lid.py             2. word-level language ID (trained CRF, rules fallback)
    features.py           CRF features shared by training and serving
    soundkey.py        3. sound keys: bahut = bohot = bht
    scripts.py         4. Devanagari / Urdu / Arabic views
    meaning.py         5. meaning + reply via an LLM fallback chain, reply checked by our LID
    llm.py                Gemini and Groq providers
models/                trained model files (lid.joblib)
ml/                    training and evaluation scripts
tests/
```
