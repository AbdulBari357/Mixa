# ML: training and evaluation

Everything here runs inside the API container, so training and serving share the exact
same tokenizer and feature code (`mixa.pipeline.tokenize`, `mixa.pipeline.features`).

## Word-level language ID (the CRF behind stage 2)

```bash
docker compose run --rm api python ml/download_lid_data.py   # public datasets -> ml/data/ (git-ignored)
docker compose run --rm api python ml/prepare_lid_data.py    # -> ml/data/prepared/*.tsv, our label set
docker compose run --rm api python ml/train_lid.py           # -> models/lid.joblib, results/lid_eval.md
```

Results: [`results/lid_eval.md`](results/lid_eval.md) (rules baseline vs CRF on four test
sets, plus an ablation showing what each data source adds).

### Data

| Source | What | Used as | License |
|---|---|---|---|
| [LinCE](https://ritual.uh.edu/lince) `lid_hineng` (Mave et al. 2018; Aguilar et al. 2020) | Hinglish tweets, human-corrected, with named entities | train; **dev = test** (official test labels are hidden) | research / non-commercial |
| [Haifa Arabizi](https://github.com/HaifaCLG/Arabizi) (Shehadi & Wintner 2022) | the only public word-labelled Arabizi + English data (Egyptian / Levantine) | 90% train / 10% test, **split by author** | no license file; research use with citation |
| [COMI-LINGUA](https://huggingface.co/datasets/LingoIITGN/COMI-LINGUA) LID (Sheth et al. 2025) | expert-annotated Hinglish; romanized rows only | train / test | CC-BY-4.0 |
| [L3Cube-HingLID](https://github.com/l3cube-pune/code-mixed-nlp) (Nayak & Joshi 2022) | pseudo-labelled Hinglish; 3,000-sentence sample, known label errors fixed | candidate only (not selected on validation) | CC BY-NC-SA 4.0 |
| [`silver/arabizi_silver.tsv`](silver/arabizi_silver.tsv) (ours) | 595 Gemini-written, Gemini-labelled Arabizi + English (+ Hinglish) chat lines. The prompt asks mostly for Emirati / Gulf dialect and Gulf spellings, but Gemini used them rarely (digit 9: 13 times, 6: twice, 8: never). Filtered by our tokenizer and against the test set | train only, never scored | ours |
| [`testsets/uae_lid.tsv`](testsets/uae_lid.tsv) (ours) | 52 sentences hand-labelled by one team member: Hinglish, Roman Urdu, Levantine/Egyptian-style Arabizi, 8 Gulf Arabizi, three-way mixes, English-only controls ([conventions](build_uae_testset.py)) | test only | ours |

Data hygiene, found by independently re-checking every dataset before training:
- COMI-LINGUA's released test set is 82% duplicated inside its train set: all test
  sentences are removed from training.
- Haifa has duplicated tweets and many sentences per author: deduplicated and split by
  author, so no one's spelling habits appear in both train and test.
- LinCE `fw` tokens include Arabic words (alaikum, yallam); sentences with `fw`,
  `ambiguous` or `unk` are dropped rather than teaching "Arabizi = other".
- Any training sentence that exactly matches a test sentence (65 found) is dropped. An
  independent audit also measured near-duplicates (retweets etc., about 1-3% of LinCE/COMI
  test sentences): removing them changes macro-F1 by less than 0.002.
- The silver generator never sees the test sentences, and silver lines that contain one or
  share a 4-word phrase with one are dropped. (A first version showed the test sentences to
  the LLM as 'reserved'; the audit caught the resulting paraphrases, so the set was regenerated.)
- No public dataset covers **Gulf** Arabizi (the digits 6 and 9 barely occur in the Haifa
  data), and our silver set only partly fills the gap (see above). The UAE test set has 8
  Gulf sentences (93.9% accuracy); beyond those, our Arabizi evidence is Levantine / Egyptian.

### Serving

`mixa.pipeline.lid.identify` is a hybrid: the CRF labels Latin-script words (where context
decides, e.g. *main* in "main gate" vs "main aa raha hoon"); Devanagari and Arabic/Urdu
script keep an exact script rule (no training set has Urdu script). Evaluation calls the same
function the API uses (`label_words`), so reported numbers are the served numbers.

## Meaning stage (LLM comparison)

```bash
docker compose run --rm api python ml/eval_meaning.py                 # all 5 models, real API quota
docker compose run --rm api python ml/eval_meaning.py --report-only   # rebuild the report, no calls
```

Results: [`results/meaning_eval.md`](results/meaning_eval.md). Earlier prompt versions are
kept next to it (`meaning_eval_v2_single_prompt.md`, `meaning_eval_v3_system_prompt.md`).
