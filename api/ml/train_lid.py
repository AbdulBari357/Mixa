"""Train and evaluate the word-level language-ID CRF.

    docker compose run --rm api python ml/prepare_lid_data.py   # raw downloads -> prepared TSVs
    docker compose run --rm api python ml/train_lid.py

Reads ml/data/prepared/<source>_<split>.tsv (one "word<TAB>label" per line, blank line
between sentences, labels already in our label set).

Protocol (test sets are never used for any choice):
  1. Hold out 10% of each human-labelled training source (LinCE, Haifa, COMI-LINGUA) as a
     validation set. HingLID (pseudo-labels) and our silver set (LLM labels) are too noisy
     to validate on.
  2. Tune the CRF's regularisation on validation, using all sources.
  3. Train each candidate mix of sources; pick the one with the best mean validation
     macro-F1.
  4. Retrain the winner on its full training data (train + validation) and score it once on
     the four test sets:
       - LinCE Hindi-English dev (LinCE's test labels are hidden, so dev is our test)
       - Haifa Arabizi+English test (Egyptian/Levantine; split by author)
       - COMI-LINGUA romanized test (every test sentence removed from training first)
       - ml/testsets/uae_lid.tsv (our hand-labelled Hinglish / Roman Urdu / Arabizi / three-way)
The model is evaluated exactly as served: predictions come from
mixa.pipeline.lid.label_words, the same function the API uses (CRF marginals for
Latin-script words, the script rule for Devanagari / Arabic-script words).
Writes models/lid.joblib and ml/results/lid_eval.{md,json}.
"""

import json
import random
import statistics
import time
from collections import Counter
from pathlib import Path

import joblib
import sklearn_crfsuite
from sklearn.metrics import classification_report, confusion_matrix

from mixa.pipeline.features import sentence_features
from mixa.pipeline.lid import _rule_label, label_words
from mixa.pipeline.tokenize import RawToken

ML_DIR = Path(__file__).parent
PREPARED = ML_DIR / "data" / "prepared"
MODEL_PATH = ML_DIR.parent / "models" / "lid.joblib"
RESULTS = ML_DIR / "results"
LABELS = ["en", "hi-ur", "ar", "ne", "other"]
SCORED = ["en", "hi-ur", "ar", "ne"]  # macro-F1 over real languages + names present in a set
GRID = [(c1, c2) for c1 in (0.05, 0.2) for c2 in (0.01, 0.1)]
VALIDATE_ON = ["lince", "haifa", "comi"]  # human-labelled sources
TESTS = {  # display name -> prepared file (the UAE set is added separately)
    "LinCE Hinglish dev": "lince_dev",
    "Haifa Arabizi test": "haifa_test",
    "COMI-LINGUA romanized test": "comi_test",
}
CANDIDATES = {
    "LinCE only": ["lince"],
    "+ Haifa Arabizi": ["lince", "haifa"],
    "+ Haifa + our silver": ["lince", "haifa", "silver"],
    "+ Haifa + silver + COMI-LINGUA": ["lince", "haifa", "silver", "comi"],
    "All sources (+ HingLID)": ["lince", "haifa", "silver", "comi", "hinglid"],
}
SEED = 13

Sentence = tuple[list[str], list[str]]


def read_tsv(path: Path) -> list[Sentence]:
    """Read "word<TAB>label" blocks separated by blank lines; "#" lines are comments."""
    sentences, words, labels = [], [], []
    for line in path.read_text(encoding="utf-8").splitlines() + [""]:
        if line.startswith("#"):
            continue
        if not line.strip():
            if words:
                sentences.append((words, labels))
            words, labels = [], []
            continue
        word, label = line.split("\t")
        if label not in LABELS:
            raise ValueError(f"{path.name}: unknown label {label!r}")
        words.append(word)
        labels.append(label)
    return sentences


def read_groups(path: Path) -> list[str]:
    return [
        line[2:].split("\t")[0] for line in path.read_text("utf-8").splitlines() if line[:2] == "# "
    ]


def train_sources() -> dict[str, list[Sentence]]:
    return {
        p.stem.removesuffix("_train"): read_tsv(p) for p in sorted(PREPARED.glob("*_train.tsv"))
    }


def split_validation(
    sources: dict[str, list[Sentence]],
) -> tuple[dict[str, list[Sentence]], dict[str, list[Sentence]]]:
    fit_part, val = {}, {}
    for name, sents in sources.items():
        if name not in VALIDATE_ON:
            fit_part[name] = sents
            continue
        shuffled = sents[:]
        random.Random(SEED).shuffle(shuffled)
        cut = int(len(shuffled) * 0.9)
        fit_part[name], val[name] = shuffled[:cut], shuffled[cut:]
    return fit_part, val


def fit(sentences: list[Sentence], c1: float, c2: float) -> sklearn_crfsuite.CRF:
    crf = sklearn_crfsuite.CRF(
        algorithm="lbfgs", c1=c1, c2=c2, max_iterations=150, all_possible_transitions=True
    )
    # Generators: CRFsuite copies each sentence in, so features never all sit in memory.
    crf.fit((sentence_features(w) for w, _ in sentences), (y for _, y in sentences))
    return crf


def crf_predict(crf) -> callable:
    """Predict exactly as served, through the API's own decoding function."""
    return lambda words: [label for label, _ in label_words(crf, words)]


def rules_predict(words: list[str]) -> list[str]:
    return [_rule_label(RawToken(w, 0, len(w), "word"))[0] for w in words]


def score(sentences: list[Sentence], predict) -> dict:
    gold = [label for _, ys in sentences for label in ys]
    pred = [label for ws, _ in sentences for label in predict(ws)]
    report = classification_report(gold, pred, labels=SCORED, output_dict=True, zero_division=0)
    present = [label for label in SCORED if report[label]["support"] > 0]
    return {
        "tokens": len(gold),
        "accuracy": round(sum(g == p for g, p in zip(gold, pred)) / len(gold), 4),
        # Average only over labels that occur in this set: a set with no Arabic must not
        # score ar as F1 = 0 (that bug halved the first run's numbers).
        "macro_f1": round(statistics.mean(report[label]["f1-score"] for label in present), 4),
        "f1": {label: round(report[label]["f1-score"], 4) for label in SCORED},
        "support": {label: int(report[label]["support"]) for label in SCORED},
        "confusion": confusion_matrix(gold, pred, labels=LABELS).tolist(),
    }


def bootstrap_accuracy_ci(sentences: list[Sentence], predict, reps: int = 2000) -> list[float]:
    """95% interval for word accuracy, resampling whole sentences (small test sets)."""
    per_sentence = []
    for words, gold in sentences:
        pred = predict(words)
        per_sentence.append((sum(g == p for g, p in zip(gold, pred)), len(gold)))
    rng, accs = random.Random(SEED), []
    for _ in range(reps):
        sample = [per_sentence[rng.randrange(len(per_sentence))] for _ in per_sentence]
        accs.append(sum(r for r, _ in sample) / sum(n for _, n in sample))
    accs.sort()
    return [round(accs[int(reps * 0.025)], 4), round(accs[int(reps * 0.975)], 4)]


def validation_score(val: dict[str, list[Sentence]], predict) -> dict[str, float]:
    scores = {name: score(sents, predict)["macro_f1"] for name, sents in val.items()}
    scores["mean"] = round(statistics.mean(scores.values()), 4)
    return scores


def pool(parts: dict[str, list[Sentence]], names: list[str]) -> list[Sentence]:
    return [s for name in names for s in parts[name]]


def uae_errors(sentences: list[Sentence], predict) -> list[str]:
    out = []
    for words, gold in sentences:
        pred = predict(words)
        wrong = [f"{w} ({g}→{p})" for w, g, p in zip(words, gold, pred) if g != p]
        if wrong:
            out.append(f"{' '.join(words)}: " + ", ".join(wrong))
    return out


def group_sizes(sentences: list[Sentence], groups: list[str]) -> dict[str, int]:
    sizes = Counter()
    for (words, _), group in zip(sentences, groups):
        sizes[group] += len(words)
    return dict(sizes)


def by_group(sentences: list[Sentence], groups: list[str], predict) -> dict[str, float]:
    right, total = Counter(), Counter()
    for (words, gold), group in zip(sentences, groups):
        pred = predict(words)
        right[group] += sum(g == p for g, p in zip(gold, pred))
        total[group] += len(gold)
    return {g: round(right[g] / total[g], 4) for g in total}


def write_report(r: dict) -> None:
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "lid_eval.json").write_text(json.dumps(r, indent=2), encoding="utf-8")
    sizes = ", ".join(f"{k} ({v})" for k, v in r["train_sizes"].items())
    lines = [
        "# Word-level language ID: rules baseline vs trained CRF",
        "",
        (
            f"**Selected model: {r['selected']}** ({r['final_sentences']} training sentences; "
            f"CRF c1={r['c1']}, c2={r['c2']}; {r['model_mb']} MB; trained in "
            f"{r['train_seconds']} s). Available sentences per source: {sizes}."
        ),
        "",
        (
            "Regularisation and the mix of training sources were chosen on validation data (10% "
            "of each human-labelled source), never on the test sets below. Scores are over word "
            "tokens (the tokenizer handles punctuation, emoji and numbers). Macro-F1 averages "
            "F1 over the labels en / hi-ur / ar / ne that occur in each test set; COMI-LINGUA "
            "has no name label, so its macro covers en / hi-ur only."
        ),
        "",
        (
            "**History.** A first run fixed the final model in advance as 'all sources' and "
            "scored it on these test sets ([lid_eval_v1_prereg.md](lid_eval_v1_prereg.md)). Its "
            "ablation showed two sources without name labels hurting names, which is why this "
            "validation protocol and the 'without HingLID' candidate were added afterwards. So "
            "the test sets are not untouched. The pre-registered all-sources model scored "
            f"{r['prereg_note']}."
        ),
        "",
        "| Test set | Words | Rules accuracy | CRF accuracy | Rules macro-F1 | CRF macro-F1 |",
        "|---|---|---|---|---|---|",
    ]
    for name, t in r["tests"].items():
        lines.append(
            f"| {name} | {t['crf']['tokens']} | {t['rules']['accuracy']:.1%} | "
            f"{t['crf']['accuracy']:.1%} | {t['rules']['macro_f1']:.3f} | {t['crf']['macro_f1']:.3f} |"
        )
    for name, t in r["tests"].items():
        lines += ["", f"## {name}: F1 per label", "", "| Label | Words | Rules | CRF |"]
        lines.append("|---|---|---|---|")
        for label in SCORED:
            if t["crf"]["support"][label]:
                lines.append(
                    f"| {label} | {t['crf']['support'][label]} | {t['rules']['f1'][label]:.3f} "
                    f"| {t['crf']['f1'][label]:.3f} |"
                )
    names = list(r["tests"])
    lines += [
        "",
        "## Which training data helps: model selection on validation",
        "",
        (
            "Each candidate is trained on 90% of its sources. The **validation** column decided "
            "the selection; the test columns are shown only to explain what each source adds."
        ),
        "",
        "| Training data | Sentences | Validation macro-F1 | " + " | ".join(names) + " |",
        "|---|---|---|" + "---|" * len(names),
    ]
    for variant, a in r["candidates"].items():
        mark = " ✅" if variant == r["selected"] else ""
        cells = " | ".join(f"{a['test_macro_f1'][n]:.3f}" for n in names)
        lines.append(
            f"| {variant}{mark} | {a['sentences']} | {a['validation']['mean']:.3f} | {cells} |"
        )
    ci = r["uae_accuracy_ci"]
    lines += [
        "",
        "## UAE test set: accuracy by message type",
        "",
        (
            f"Small set ({r['tests']['UAE hand-labelled']['crf']['tokens']} words, labelled by one "
            f"team member): CRF accuracy 95% interval {ci[0]:.1%} to {ci[1]:.1%} (sentence "
            "bootstrap). Its macro-F1 rests on very few name tokens, so read accuracy and the "
            "language F1s instead. Silver training data was generated without showing these "
            "sentences to the LLM, and silver lines that contain one or share a 4-word phrase "
            "with one are removed."
        ),
        "",
        "| Type | Words | Rules | CRF |",
        "|---|---|---|---|",
    ]
    for g, acc in r["uae_groups"]["crf"].items():
        n = r["uae_group_sizes"][g]
        lines.append(f"| {g} | {n} | {r['uae_groups']['rules'][g]:.1%} | {acc:.1%} |")
    lines += ["", "## UAE test set: every CRF error", ""]
    lines += [f"- {e}" for e in r["uae_crf_errors"]] or ["- none"]
    (RESULTS / "lid_eval.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sources = train_sources()
    needed = {src for srcs in CANDIDATES.values() for src in srcs}
    if needed - sources.keys():
        raise SystemExit(f"Missing prepared data for {needed - sources.keys()}.")
    fit_part, val = split_validation(sources)
    print("Validation sentences:", {k: len(v) for k, v in val.items()})

    everything = list(CANDIDATES.values())[-1]
    print("Tuning regularisation on validation (all sources):")
    trials = []
    for c1, c2 in GRID:
        v = validation_score(val, crf_predict(fit(pool(fit_part, everything), c1, c2)))
        trials.append({"c1": c1, "c2": c2, "validation": v})
        print(f"  c1={c1} c2={c2}: {v}")
    best = max(trials, key=lambda t: t["validation"]["mean"])
    c1, c2 = best["c1"], best["c2"]

    uae_path = ML_DIR / "testsets" / "uae_lid.tsv"
    uae = read_tsv(uae_path)
    tests = {name: read_tsv(PREPARED / f"{f}.tsv") for name, f in TESTS.items()}
    tests["UAE hand-labelled"] = uae

    print("Candidate training mixes:")
    candidates = {}
    for variant, names in CANDIDATES.items():
        subset = pool(fit_part, names)
        predict = crf_predict(fit(subset, c1, c2))
        candidates[variant] = {
            "sources": names,
            "sentences": len(subset),
            "validation": validation_score(val, predict),
            "test_macro_f1": {n: score(s, predict)["macro_f1"] for n, s in tests.items()},
        }
        print(f"  {variant}: validation {candidates[variant]['validation']}")
    selected = max(candidates, key=lambda k: candidates[k]["validation"]["mean"])
    print(f"Selected on validation: {selected}")

    final_data = pool(sources, CANDIDATES[selected])  # train + validation
    start = time.monotonic()
    final = fit(final_data, c1, c2)
    train_seconds = round(time.monotonic() - start, 1)
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(final, MODEL_PATH, compress=3)

    predict = crf_predict(final)
    groups = read_groups(uae_path)
    report = {
        "selected": selected,
        "final_sentences": len(final_data),
        "train_sizes": {k: len(v) for k, v in sources.items()},
        "c1": c1,
        "c2": c2,
        "tuning": trials,
        "candidates": candidates,
        "train_seconds": train_seconds,
        "model_mb": round(MODEL_PATH.stat().st_size / 1e6, 1),
        "tests": {
            name: {"rules": score(sents, rules_predict), "crf": score(sents, predict)}
            for name, sents in tests.items()
        },
        "uae_groups": {
            "rules": by_group(uae, groups, rules_predict),
            "crf": by_group(uae, groups, predict),
        },
        "uae_crf_errors": uae_errors(uae, predict),
        "uae_group_sizes": group_sizes(uae, groups),
        "uae_accuracy_ci": bootstrap_accuracy_ci(uae, predict),
        # Recorded by the independent audit (full-data retrain of the pre-registered mix).
        "prereg_note": "0.862 / 0.814 / 0.922 / 0.861 macro-F1 on LinCE / Haifa / COMI / UAE",
    }
    write_report(report)
    for name, t in report["tests"].items():
        print(
            f"{name}: rules acc {t['rules']['accuracy']} F1 {t['rules']['macro_f1']} | "
            f"CRF acc {t['crf']['accuracy']} F1 {t['crf']['macro_f1']}"
        )
    print(f"Saved {MODEL_PATH} ({report['model_mb']} MB)")


if __name__ == "__main__":
    main()
