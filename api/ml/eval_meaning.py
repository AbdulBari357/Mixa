"""Compare LLMs for the meaning stage.

For each model: how often it answered, latency, and whether its reply keeps the
sender's language mix ("register"), judged by our own language ID, not by the LLM.
Scoring uses the same rules as production (mixa.pipeline.meaning): an echo of the
message never counts as keeping the register.

    docker compose run --rm api python ml/eval_meaning.py [provider:model ...]
    docker compose run --rm api python ml/eval_meaning.py --report-only   # no API calls

Uses real free-tier quota (13 calls per model) and is paced to stay under each
provider's per-minute limits. Writes ml/results/meaning_eval.{md,json}.
All messages are synthetic: never put real chats here (free tiers may train on them).
"""

import json
import statistics
import sys
import time
from pathlib import Path

from pydantic import ValidationError

from mixa.config import get_settings
from mixa.pipeline import analyze
from mixa.pipeline.lid import identify
from mixa.pipeline.llm import build_provider
from mixa.pipeline.meaning import (
    PROMPT_VERSION,
    SYSTEM_PROMPT,
    build_user_prompt,
    keeps_register,
    normalise,
)
from mixa.pipeline.tokenize import tokenize

MESSAGES = [
    ("hinglish", "yaar aaj office nahi aa paunga, tabiyat thodi kharab hai"),
    ("hinglish", "kal ka exam postpone ho gaya kya? mujhe kisi ne bataya nahi"),
    ("hinglish", "bhai ye laptop bohot slow chal raha hai, kya karun"),
    ("hinglish", "didi mummy ne bola dinner pe jaldi aana, guests aa rahe hain"),
    ("roman-urdu", "yar meri flight delay ho gayi hai, pickup ke liye thora wait karna parega"),
    ("roman-urdu", "aap ki baat theek hai lekin meri salary abhi tak nahi aayi"),
    ("roman-urdu", "kya scene hai weekend ka? beach chalein ya mall?"),
    ("arabizi", "habibi ana wa9alt, wainak? I'm at the main gate"),
    ("arabizi", "wallah el traffic kan kteer today, sorry ta2akhart"),
    ("arabizi", "yalla guys, 3ndi meeting ba3d nus sa3a, call me later inshallah"),
    ("three-way", "bhai kal meeting hai, ana coming ba3d shwaya, traffic bohot hai"),
    ("three-way", "khalas yaar, I'm done for today, kal baat karte hain inshallah"),
    ("english-control", "Can you send me the report before 5pm?"),
]

# (spec, seconds between calls): Gemini free = 15 RPM; Groq free ~8K tokens/min per model.
CANDIDATES = [
    ("gemini:gemini-3.5-flash-lite", 4.5),
    ("groq:openai/gpt-oss-120b", 6.0),
    ("gemini:gemini-3.1-flash-lite", 4.5),
    ("groq:openai/gpt-oss-20b", 6.0),
    ("groq:qwen/qwen3.8-27b", 6.0),
]
OUT_DIR = Path(__file__).parent / "results"


def non_english_share(reply: str) -> float:
    labels = [lang for lang, _ in identify(tokenize(reply))[0] if lang in ("en", "hi-ur", "ar")]
    return sum(lang != "en" for lang in labels) / len(labels) if labels else 0.0


def call_once(provider, text: str, tags: list[tuple[str, str]]) -> dict:
    start = time.monotonic()
    m = provider.generate(SYSTEM_PROMPT, build_user_prompt(text, tags))
    echo = normalise(m.reply) == normalise(text)
    return {
        "ok": True,
        "latency_s": round(time.monotonic() - start, 2),
        "en": m.en,
        "reply": m.reply,
        "echo": echo,
        "register_kept": not echo and keeps_register({lang for _, lang in tags}, m.reply),
        "non_english_share": round(non_english_share(m.reply), 2),
    }


def run_model(spec: str, pause: float) -> list[dict]:
    s = get_settings()
    provider = build_provider(spec, s.gemini_api_key, s.groq_api_key, s.llm_timeout_s)
    if provider is None:
        print(f"skip {spec}: no API key")
        return []
    rows = []
    for group, text in MESSAGES:
        tags = [
            (t.text, t.lang)
            for t in analyze(text, with_meaning=False).tokens
            if t.lang not in ("other", "ne")
        ]
        row = {"model": provider.name, "group": group, "message": text}
        for attempt in (1, 2):
            try:
                row |= call_once(provider, text, tags)
                row.pop("error", None)  # clear a failed first attempt (429 retry)
                row.pop("error_kind", None)
                break
            except ValidationError:
                row |= {"ok": False, "error": "invalid JSON", "error_kind": "json"}
                break
            except Exception as e:  # noqa: BLE001 - record any failure and move on
                status = getattr(e, "code", None) or getattr(
                    getattr(e, "response", None), "status_code", None
                )
                error = f"{type(e).__name__} {status or ''}".strip()
                row |= {"ok": False, "error": error, "error_kind": "api"}
                if status == 429 and attempt == 1:
                    time.sleep(30)  # measure the model, not the rate limit
                    continue
                break
        rows.append(row)
        mark = "ok " if row["ok"] else "ERR"
        print(
            f"  {mark} {provider.name:24} {row.get('latency_s', '-'):>5}s  "
            f"{row.get('reply', row.get('error'))}"
        )
        time.sleep(pause)
    return rows


def summarise(rows: list[dict]) -> dict:
    ok = [r for r in rows if r["ok"]]
    mixed = [r for r in ok if r["group"] != "english-control"]
    lat = sorted(r["latency_s"] for r in ok)
    share = [r["non_english_share"] for r in mixed]
    return {
        "answered": f"{len(ok)}/{len(rows)}",
        "json_errors": sum(r.get("error_kind") == "json" for r in rows),
        "api_errors": sum(r.get("error_kind") == "api" for r in rows),
        "median_latency_s": round(statistics.median(lat), 2) if lat else None,
        "max_latency_s": lat[-1] if lat else None,
        "register_kept": f"{sum(r['register_kept'] for r in mixed)}/{len(mixed)}",
        "avg_non_english_share": round(statistics.mean(share), 2) if share else None,
        "echoes": sum(r["echo"] for r in ok),
    }


def write_report(all_rows: list[dict]) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "meaning_eval.json").write_text(
        json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    models = list(dict.fromkeys(r["model"] for r in all_rows))
    lines = [
        "# Meaning stage: LLM comparison",
        "",
        (
            f"Prompt version {PROMPT_VERSION}. {len(MESSAGES)} synthetic messages (Hinglish, "
            "Roman Urdu, Arabizi, three-way mixes, 1 English control). *Register kept* = our "
            "language ID finds a non-English language the sender used in the reply to a mixed "
            "message (an echo of the message never counts). Our ID is still the rules baseline, "
            "so read the replies below too. *API errors* are provider failures (e.g. 503), not "
            "model output problems."
        ),
        "",
        (
            "| Model | Answered | JSON errors | API errors | Median latency | Max latency "
            "| Register kept | Avg non-English share | Echoes |"
        ),
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for model in models:
        s = summarise([r for r in all_rows if r["model"] == model])
        lines.append(
            f"| {model} | {s['answered']} | {s['json_errors']} | {s['api_errors']} "
            f"| {s['median_latency_s']} s | {s['max_latency_s']} s | {s['register_kept']} "
            f"| {s['avg_non_english_share']} | {s['echoes']} |"
        )
    lines += ["", "## Replies", ""]
    for _, text in MESSAGES:
        lines += [f"**{text}**", ""]
        for r in (r for r in all_rows if r["message"] == text):
            if r["ok"]:
                flag = " ⚠️ echo" if r["echo"] else ("" if r["register_kept"] else " ⚠️ English")
                lines.append(f"- `{r['model']}`{flag}: {r['reply']}  \n  _{r['en']}_")
            else:
                lines.append(f"- `{r['model']}`: error {r['error']}")
        lines.append("")
    (OUT_DIR / "meaning_eval.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = sys.argv[1:]
    if args == ["--report-only"]:
        all_rows = json.loads((OUT_DIR / "meaning_eval.json").read_text(encoding="utf-8"))
    else:
        candidates = [c for c in CANDIDATES if not args or c[0] in args]
        all_rows = []
        if args:  # rerunning some models: keep the other models' rows from the last run
            rerun = {spec.partition(":")[2] for spec, _ in candidates}
            previous = json.loads((OUT_DIR / "meaning_eval.json").read_text(encoding="utf-8"))
            all_rows = [r for r in previous if r["model"] not in rerun]
        for spec, pause in candidates:
            print(f"== {spec}")
            all_rows += run_model(spec, pause)
        order = [spec.partition(":")[2] for spec, _ in CANDIDATES]
        all_rows.sort(key=lambda r: order.index(r["model"]) if r["model"] in order else len(order))
    write_report(all_rows)
    for model in dict.fromkeys(r["model"] for r in all_rows):
        print(model, summarise([r for r in all_rows if r["model"] == model]))


if __name__ == "__main__":
    main()
