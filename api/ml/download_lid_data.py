"""Download the public datasets used to train the language-ID model into ml/data/.

    docker compose run --rm api python ml/download_lid_data.py

The data is not committed (licenses below don't allow redistribution); this script
fetches the exact versions we used. All sources are for research / non-commercial use:
cite them if you use this model.

  LinCE lid_hineng   Mave et al. 2018; Aguilar et al. 2020. Research / non-commercial.
                     Hugging Face parquet mirror, repo sha 88298d41.
  Haifa Arabizi      Shehadi & Wintner 2022 (WANLP). No license file: research use with citation.
  COMI-LINGUA LID    Sheth, Beniwal & Singh 2025 (EMNLP Findings). CC-BY-4.0. Pinned revision.
  L3Cube-HingLID     Nayak & Joshi 2022. CC BY-NC-SA 4.0.
"""

from pathlib import Path

import pandas as pd
import requests

DATA = Path(__file__).parent / "data"

LINCE = "https://huggingface.co/datasets/lince-benchmark/lince/resolve/refs%2Fconvert%2Fparquet/lid_hineng/{split}/0000.parquet"
FILES = {
    "haifa_arabizi/words_annotated.csv": "https://raw.githubusercontent.com/HaifaCLG/Arabizi/main/words_annotated.csv",
    "comi_lingua/LID_train.csv": "https://huggingface.co/datasets/LingoIITGN/COMI-LINGUA/resolve/0214cb358e59e36da60e01d3d59ddd24df897749/LID_train.csv",
    "comi_lingua/LID_test.csv": "https://huggingface.co/datasets/LingoIITGN/COMI-LINGUA/resolve/0214cb358e59e36da60e01d3d59ddd24df897749/LID_test.csv",
    "l3cube_hinglid/train.txt": "https://raw.githubusercontent.com/l3cube-pune/code-mixed-nlp/main/L3Cube-HingLID/train.txt",
}  # fmt: skip


def fetch(url: str, dest: Path) -> None:
    if dest.exists():
        print(f"have   {dest.relative_to(DATA)}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        tmp = dest.with_suffix(dest.suffix + ".part")
        with tmp.open("wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
        tmp.rename(dest)
    print(f"got    {dest.relative_to(DATA)}")


def lince() -> None:
    # Parquet (one row per sentence) -> CoNLL ("token<TAB>label", blank line between sentences).
    for split, name in (("train", "train"), ("validation", "dev")):
        parquet = DATA / "lince" / "lid_hineng" / f"{split}.parquet"
        fetch(LINCE.format(split=split), parquet)
        conll = parquet.with_name(f"{name}.conll")
        if conll.exists():
            continue
        df = pd.read_parquet(parquet)
        lines = []
        for words, labels in zip(df.words, df.lid):
            lines += [f"{w}\t{label}" for w, label in zip(words, labels)] + [""]
        conll.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"wrote  {conll.relative_to(DATA)}")


def main() -> None:
    lince()
    for rel, url in FILES.items():
        fetch(url, DATA / rel)


if __name__ == "__main__":
    main()
