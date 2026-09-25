"use client";

import { useState } from "react";
import { analyze } from "@/lib/api";
import type { AnalyzeResponse, Lang } from "@/lib/types";

const LANG_STYLE: Record<Lang, { label: string; className: string }> = {
  en: { label: "English", className: "bg-sky-100 text-sky-900 dark:bg-sky-900/40 dark:text-sky-100" },
  "hi-ur": { label: "Hindi/Urdu", className: "bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-100" },
  ar: { label: "Arabic", className: "bg-emerald-100 text-emerald-900 dark:bg-emerald-900/40 dark:text-emerald-100" },
  ne: { label: "Name", className: "bg-violet-100 text-violet-900 dark:bg-violet-900/40 dark:text-violet-100" },
  other: { label: "Other", className: "text-zinc-500" },
};

const EXAMPLES = [
  "bhai kal meeting hai, ana coming ba3d shwaya, traffic bohot hai",
  "mujhe samaj nhi ara kya horaha hai",
  "yalla guys, I'll be late inshallah 😂",
];

export default function Home() {
  const [text, setText] = useState(EXAMPLES[0]);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    try {
      setResult(await analyze(text));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-8 px-4 py-12">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight">Mixa</h1>
        <p className="mt-2 text-zinc-600 dark:text-zinc-400">
          Write the way you actually talk. Mixa understands mixed languages, spelling by ear and
          borrowed scripts without correcting you.
        </p>
      </header>

      <section className="flex flex-col gap-3">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={3}
          className="w-full rounded-lg border border-zinc-300 bg-transparent p-3 dark:border-zinc-700"
          aria-label="Message to analyze"
        />
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={run}
            disabled={loading || !text.trim()}
            className="rounded-lg bg-zinc-900 px-4 py-2 text-white disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900"
          >
            {loading ? "Reading…" : "Analyze"}
          </button>
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              onClick={() => setText(ex)}
              className="rounded-full border border-zinc-300 px-3 py-1 text-sm text-zinc-600 dark:border-zinc-700 dark:text-zinc-400"
            >
              {ex.slice(0, 24)}…
            </button>
          ))}
        </div>
        {error && <p className="text-sm text-red-600">{error}. Is the API running?</p>}
      </section>

      {result && (
        <section className="flex flex-col gap-6">
          <div className="flex flex-wrap gap-2">
            {result.tokens.map((t, i) => (
              <span
                key={i}
                title={`${LANG_STYLE[t.lang].label} · ${Math.round(t.conf * 100)}%${t.key ? ` · key ${t.key}` : ""}`}
                className={`flex flex-col items-center rounded-md px-2 py-1 ${LANG_STYLE[t.lang].className}`}
              >
                <span className="font-medium">{t.text}</span>
                {Object.values(t.scripts)[0] && Object.values(t.scripts)[0] !== t.text && (
                  <span className="text-xs opacity-80">{Object.values(t.scripts).join(" · ")}</span>
                )}
              </span>
            ))}
          </div>

          <dl className="grid grid-cols-3 gap-4 text-center">
            <div>
              <dt className="text-sm text-zinc-500">Languages</dt>
              <dd className="text-lg font-medium">
                {result.stats.languages.map((l) => LANG_STYLE[l].label).join(" + ")}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-zinc-500">Switch points</dt>
              <dd className="text-lg font-medium">{result.stats.switch_points}</dd>
            </div>
            <div>
              <dt className="text-sm text-zinc-500">Code-Mixing Index</dt>
              <dd className="text-lg font-medium">{result.stats.cmi}</dd>
            </div>
          </dl>

          {result.meaning ? (
            <div className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
              <p>{result.meaning.en}</p>
              <p className="mt-2 text-sm text-zinc-500">In your words: {result.meaning.same_register}</p>
            </div>
          ) : (
            <p className="text-sm text-zinc-500">Meaning unavailable (no Gemini key configured).</p>
          )}

          <p className="text-xs text-zinc-400">
            Language ID: {result.lid_source === "model" ? "trained model" : "rules baseline"}
          </p>
        </section>
      )}
    </main>
  );
}
