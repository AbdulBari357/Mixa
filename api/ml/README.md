# ML: training and evaluation

Everything here runs inside the API container so training and serving share the
exact same feature code (`mixa.pipeline.features`).

```bash
docker compose run --rm api python ml/train_lid.py
```

## Plan

| Step | Output | Status |
|---|---|---|
| Get LinCE Hindi-English LID data into `ml/data/lince/` | train/dev files | todo |
| Map LinCE labels -> ours (`lang1`->`en`, `lang2`->`hi-ur`, `ne`, rest -> `other`) | | todo |
| Arabizi: ~300 labelled words/sentences in `ml/data/arabizi/` (hand-checked) | | todo |
| `train_lid.py`: CRF on `sentence_features`, save `models/lid.joblib` | model | todo |
| `eval_lid.py`: per-label P/R/F1 on LinCE dev, rules baseline vs model | numbers for README | todo |
| Dakshina `hi`/`ur` romanization lexicons -> sound-key grouping precision/recall | numbers for README | todo |

`ml/data/` is git-ignored; document any download steps in this file instead.
