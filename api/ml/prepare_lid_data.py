"""Convert the downloaded datasets into ml/data/prepared/<source>_<split>.tsv for train_lid.py.

    docker compose run --rm api python ml/prepare_lid_data.py

Every raw token is re-split with OUR tokenizer and only word tokens are kept (at inference
punctuation, emoji and numbers never reach the model). Labels are mapped to ours:
en, hi-ur, ar, ne, other.

Sources (downloaded into ml/data/, which is git-ignored; see ml/README.md for how):
  lince    LinCE lid_hineng (Mave et al. 2018; Aguilar et al. 2020). Hinglish tweets,
           human-corrected, with named entities. Research / non-commercial use.
           Test labels are hidden, so dev is our held-out test.
  haifa    Haifa Arabizi code-switching corpus (Shehadi & Wintner 2022). The only public
           word-labelled Arabizi+English data (Egyptian/Levantine). No license file:
           research use with citation. Split 80/10/10 BY AUTHOR (train = train + dev).
  comi     COMI-LINGUA LID (Sheth et al. 2025), CC-BY-4.0. Romanized (Latin-only) rows.
           82% of the released test set is duplicated in train, so every test sentence
           is removed from train before use.
  hinglid  L3Cube-HingLID (Nayak & Joshi 2022), CC BY-NC-SA 4.0. Pseudo-labelled and
           keyword-selected, so only a 3,000-sentence sample with known label errors fixed.
  silver   ml/silver/arabizi_silver.tsv: our Gemini-labelled Gulf/Levantine/Egyptian
           Arabizi + English (+ Hinglish) sentences. Training only.
Finally, any training sentence that also appears in a test set is dropped.
"""

import ast
import collections
import csv
import random
import re
import sys
from pathlib import Path

from mixa.pipeline.tokenize import tokenize

ML_DIR = Path(__file__).parent
RAW = ML_DIR / "data"
OUT = RAW / "prepared"
SEED = 13
csv.field_size_limit(sys.maxsize)

Sentence = tuple[list[str], list[str]]


def words_only(tokens: list[str], labels: list[str]) -> Sentence:
    """Re-split raw tokens with our tokenizer; keep word pieces with their token's label."""
    words, out = [], []
    for token, label in zip(tokens, labels):
        for piece in tokenize(token):
            if piece.kind == "word":
                words.append(piece.text)
                out.append(label)
    return words, out


# --- LinCE ------------------------------------------------------------------------------
# fw holds Arabic-origin Latin words (alaikum, yallam): mapping it to "other" would teach
# the model that Arabizi is "other", so sentences with fw/ambiguous/unk are dropped.
LINCE_MAP = {"lang1": "en", "lang2": "hi-ur", "ne": "ne", "other": "other", "mixed": "hi-ur"}


def lince(split: str) -> list[Sentence]:
    path = RAW / "lince" / "lid_hineng" / f"{split}.conll"
    out, toks, raw = [], [], []
    for line in path.read_text(encoding="utf-8").splitlines() + [""]:
        if line.startswith("# sent_enum"):
            continue
        if not line:
            if toks and all(r in LINCE_MAP for r in raw):
                out.append(words_only(toks, [LINCE_MAP[r] for r in raw]))
            toks, raw = [], []
            continue
        tok, _, lab = line.partition("\t")
        toks.append(tok)
        raw.append(lab)
    return out


# --- Haifa Arabizi ----------------------------------------------------------------------
HAIFA_MAP = {"0": "ar", "1": "en", "2": "fr", "3": "ar", "4": "ne", "5": "other"}
# "Shared" (4) mixes names with culture words and loanwords; map the known ones.
LOAN_AR = {"allah", "inshallah", "insha", "mashallah", "halal", "haram", "ramadan", "habibi",
           "yalla", "wallah", "shawarma", "shawerma", "3arab", "nchalla", "ikhwan"}  # fmt: skip
LOAN_EN = {"twitter", "online", "video", "youtube", "instagram", "ig", "facebook", "internet",
           "trend", "gym", "zoom", "camera", "mobile", "bank", "billion", "lemon", "sushi",
           "wikipedia"}  # fmt: skip


def _haifa_label(token: str, categ: str) -> str:
    if categ != "4":
        return HAIFA_MAP[categ]
    low = token.lower()
    if low in LOAN_AR:
        return "ar"
    if low in LOAN_EN:
        return "en"
    return "ne" if any(c.isalpha() for c in token) else "other"


def haifa() -> dict[str, list[Sentence]]:
    sents, seen, cur = [], set(), None
    rows = csv.DictReader((RAW / "haifa_arabizi" / "words_annotated.csv").open(encoding="utf-8"))
    for r in [*rows, None]:
        key = r and (r["source"], r["sen_id"], r["sen_num"])
        if cur and (r is None or key != cur["key"]):  # a sentence = a contiguous run of one key
            dedupe_key = tuple(t.lower() for t in cur["tokens"])
            if "fr" not in cur["labels"] and dedupe_key not in seen:  # drop French, duplicates
                seen.add(dedupe_key)
                sents.append(cur)
            cur = None
        if r is None:
            break
        if cur is None:
            cur = {"key": key, "tokens": [], "labels": [], "user": (r["source"], r["user_name"])}
        cur["tokens"].append(r["token"])
        cur["labels"].append(_haifa_label(r["token"], r["categ"].strip()))

    # 80/10/10 split by author, stratified by source: no author is in both train and test.
    rng = random.Random(SEED)
    split = {"train": [], "test": []}
    for source in sorted({s["key"][0] for s in sents}):
        users = sorted({s["user"] for s in sents if s["key"][0] == source})
        rng.shuffle(users)
        test_users = set(users[int(len(users) * 0.9) :])
        for s in (s for s in sents if s["key"][0] == source):
            part = "test" if s["user"] in test_users else "train"
            split[part].append(words_only(s["tokens"], s["labels"]))
    return split


# --- COMI-LINGUA ------------------------------------------------------------------------
COMI_MAP = {"hi": "hi-ur", "h": "hi-ur", "en": "en", "e": "en", "ot": "other", "o": "other",
            "u": "other"}  # fmt: skip
DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def _comi_cell(cell: str):
    try:
        items = ast.literal_eval(cell)
    except (ValueError, SyntaxError):
        return None
    return [(d["key"], d["value"]) if isinstance(d, dict) else (d[0], d[1]) for d in items] or None


def _read_comi(path: Path, exclude: frozenset[str] = frozenset()) -> list[Sentence]:
    out = []
    with path.open(encoding="utf-8", newline="") as f:
        rows = csv.reader(f)
        next(rows)
        for row in rows:
            sent = row[0].strip()
            if sent in exclude or DEVANAGARI.search(sent):  # de-leak; romanized rows only
                continue
            anns = [a for a in map(_comi_cell, row[2:5]) if a]
            if not anns:
                continue
            # Majority tokenization, then a per-token majority vote over the 3 annotators.
            cands = collections.Counter(tuple(w for w, _ in a) for a in anns)
            key = max(
                cands,
                key=lambda k: (cands[k], "".join(k).replace(" ", "") == sent.replace(" ", "")),
            )
            same = [a for a in anns if tuple(w for w, _ in a) == key]
            try:
                labels = [
                    collections.Counter(COMI_MAP[a[i][1]] for a in same).most_common(1)[0][0]
                    for i in range(len(key))
                ]
            except KeyError:
                continue
            out.append(words_only(list(key), labels))
    return out


def comi() -> dict[str, list[Sentence]]:
    base = RAW / "comi_lingua"
    with (base / "LID_test.csv").open(encoding="utf-8", newline="") as f:
        test_sents = frozenset(row[0].strip() for row in list(csv.reader(f))[1:])
    return {
        "train": _read_comi(base / "LID_train.csv", exclude=test_sents),
        "test": _read_comi(base / "LID_test.csv"),
    }


# --- L3Cube-HingLID ---------------------------------------------------------------------
# Hindi abbreviations the pseudo-labeller systematically tagged EN (h = hai, kr = kar, ...).
HINGLID_FIX_HI = {"h", "kr", "pr", "sb", "ky", "mn", "logo"}
HINGLID_JUNK = {"amp", "pic", "rt", "com", "https", "http", "www", "twitter"}


def hinglid(n: int = 3000) -> list[Sentence]:
    sents, toks, labs = [], [], []
    path = RAW / "l3cube_hinglid" / "train.txt"
    for line in path.read_text(encoding="utf-8").splitlines() + [""]:
        if not line.strip():
            if toks:
                sents.append((toks, labs))
            toks, labs = [], []
            continue
        word, label = line.split("\t")
        if word in HINGLID_JUNK or len(word) >= 15:  # URL bits, glued hashtag bodies
            continue
        toks.append(word)
        labs.append("hi-ur" if word in HINGLID_FIX_HI else {"HI": "hi-ur", "EN": "en"}[label])
    random.Random(SEED).shuffle(sents)
    return [words_only(t, l) for t, l in sents[:n]]


# --- ours -------------------------------------------------------------------------------
def read_tsv(path: Path) -> list[Sentence]:
    out, words, labels = [], [], []
    for line in path.read_text(encoding="utf-8").splitlines() + [""]:
        if line.startswith("#"):
            continue
        if not line.strip():
            if words:
                out.append((words, labels))
            words, labels = [], []
            continue
        w, label = line.split("\t")
        words.append(w)
        labels.append(label)
    return out


def write(name: str, sentences: list[Sentence]) -> None:
    sentences = [(w, lab) for w, lab in sentences if w]
    lines = []
    for words, labels in sentences:
        lines += [f"{w}\t{label}" for w, label in zip(words, labels)] + [""]
    (OUT / f"{name}.tsv").write_text("\n".join(lines), encoding="utf-8")
    counts = collections.Counter(label for _, ls in sentences for label in ls)
    print(f"{name:22} {len(sentences):6} sentences  {sum(counts.values()):7} words  {dict(counts)}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.tsv"):
        old.unlink()
    h, c = haifa(), comi()
    tests = {
        "lince_dev": lince("dev"),
        "haifa_test": h["test"],
        "comi_test": c["test"],
    }
    trains = {
        "lince_train": lince("train"),
        "haifa_train": h["train"],
        "comi_train": c["train"],
        "hinglid_train": hinglid(),
        "silver_train": read_tsv(ML_DIR / "silver" / "arabizi_silver.tsv"),
    }
    # No test sentence (including our UAE set) may appear in any training source.
    uae = read_tsv(ML_DIR / "testsets" / "uae_lid.tsv")
    test_keys = {" ".join(w).lower() for sents in [*tests.values(), uae] for w, _ in sents}
    for name, sents in trains.items():
        kept = [s for s in sents if " ".join(s[0]).lower() not in test_keys]
        if len(kept) < len(sents):
            print(f"{name}: dropped {len(sents) - len(kept)} sentences that are in a test set")
        trains[name] = kept
    for name, sents in {**trains, **tests}.items():
        write(name, sents)


if __name__ == "__main__":
    main()
