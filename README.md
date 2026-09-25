# Mixa

**Write the way you actually talk.** Mixa understands messages that mix languages
mid-sentence, spell words by ear, and write one language in another's script, and
it does this *without correcting them* to an "official" form.

> Built at BitNBuild '26 (UAE Regional Qualifying Round), 25–26 September 2026.
> Problem statement (AI/ML): *Code-Switching and Spelling by Ear.*

```
bhai kal meeting hai, ana coming ba3d shwaya, traffic bohot hai
└─ Hindi/Urdu ─┘ └ en ┘      └ ar ┘ └ en ┘ └─ ar ─┘  └ en ┘ └ Hindi/Urdu ┘
```

## Why

Language tools learn one clean version of each language. Real people, especially in
multilingual places like the UAE, write Hinglish, Roman Urdu and Arabizi (`7abibi`,
`ba3d`), switch language mid-sentence, and spell by sound (`bohot`, `bahut`, `bht`).
Spell-checkers flag all of it as wrong. Mixa treats it as valid language.

## How it works

A five-stage pipeline (details in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)):

1. **Tokenizer**: keeps `7abibi`, `ba3d`, `भाई`, `I'll` whole.
2. **Word-level language ID**: a CRF we train on code-switched data (LinCE Hinglish, Haifa
   Arabizi, COMI-LINGUA and our own synthetic Arabizi set).
3. **Sound keys**: group spellings by ear (`bahut = bohot = bht`).
4. **Script views**: show romanized words in Devanagari / Urdu / Arabic script.
5. **Meaning**: an LLM (Gemini, with Groq as fallback) reads the text *plus our tags*, explains
   it in English and replies in the writer's own mix. **Our own language ID then checks the
   reply** and tries the next model if it slipped into plain English.
   [Model comparison →](api/ml/results/meaning_eval.md)

## Results

**Word-level language ID** (our CRF vs a rules baseline; accuracy / macro-F1 over word tokens):

| Test set | Words | Rules | Mixa model |
|---|---|---|---|
| LinCE Hinglish (public benchmark) | 13,422 | 74.0% / 0.44 | **94.3% / 0.88** |
| Haifa Arabizi + English (unseen authors) | 2,125 | 76.9% / 0.50 | **92.0% / 0.80** |
| COMI-LINGUA romanized Hinglish | 16,664 | 47.7% / 0.51 | **92.1% / 0.92** |
| Our UAE set: Hinglish, Roman Urdu, Arabizi, Gulf, three-way | 361 | 79.8% / 0.61 | **94.5%** (95% CI 92–97%) / 0.88 |

Known weaknesses: names (F1 0.5–0.7); Arabic words inside a Hindi sentence (three-way
messages 88.5%); English words that are also Hindi words (*main*, *to*). Full report, data
sources and protocol: [`api/ml/results/lid_eval.md`](api/ml/results/lid_eval.md).
An independent audit reproduced every number of the previous run and found issues we then
fixed (a test-set leak into our synthetic training data, an eval/serving decoding mismatch);
the numbers above come from the retrained model. See [`api/ml/README.md`](api/ml/README.md).

**Meaning stage**: 5 free LLMs compared on 13 mixed messages:
[`api/ml/results/meaning_eval.md`](api/ml/results/meaning_eval.md).

## Run it locally

**API** (Python, runs in Docker):

```bash
cp api/.env.example api/.env        # then add GEMINI_API_KEY and/or GROQ_API_KEY (both free, optional)
docker compose up --build           # http://localhost:8000/docs
docker compose run --rm api pytest  # tests
```

**Web** (Next.js):

```bash
cd web
cp .env.example .env.local
npm install
npm run dev                         # http://localhost:3000
```

Set `NEXT_PUBLIC_USE_MOCK=1` in `web/.env.local` to work on the UI without the API.

> **Privacy:** messages you analyze are sent to the Google Gemini / Groq free tiers, which
> may use them to improve their services. Don't paste private chats.

## Repository layout

```
api/     FastAPI service + ML pipeline (Python 3.12, uv)
  ml/    training and evaluation scripts
web/     Next.js frontend
docs/    architecture and decisions
```

## Team

- Umair Raizan ([@umairai21](https://github.com/umairai21))
- Abdul Bari Mohammed ([@AbdulBari357](https://github.com/AbdulBari357))
