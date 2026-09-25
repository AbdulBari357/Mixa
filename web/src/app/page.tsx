"use client";

import { useEffect, useState } from "react";
import { analyze, getProviders } from "@/lib/api";
import type { AnalyzeResponse, Lang, ProviderOption } from "@/lib/types";

const LANG_STYLE: Record<Lang, { label: string; className: string }> = {
  en: { label: "English", className: "bg-sky-100 text-sky-900 dark:bg-sky-900/40 dark:text-sky-100" },
  "hi-ur": { label: "Hindi/Urdu", className: "bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-100" },
  ar: { label: "Arabic", className: "bg-emerald-100 text-emerald-900 dark:bg-emerald-900/40 dark:text-emerald-100" },
  ne: { label: "Name", className: "bg-violet-100 text-violet-900 dark:bg-violet-900/40 dark:text-violet-100" },
  other: { label: "Other", className: "text-zinc-500" },
};

const AUTO_OPTION: ProviderOption = { id: "auto", label: "Auto (best available, with fallback)", vendor: "" };
const PROVIDER_KEY = "mixa.provider";
const MAX_CHARS = 500;

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
  const [providers, setProviders] = useState<ProviderOption[]>([AUTO_OPTION]);
  const [provider, setProvider] = useState(AUTO_OPTION.id);

  // Load the models the API has keys for, then restore this browser's last choice if still offered.
  useEffect(() => {
    getProviders()
      .then(({ options, default: fallback }) => {
        setProviders(options);
        let saved: string | null = null;
        try {
          saved = localStorage.getItem(PROVIDER_KEY);
        } catch {}
        setProvider(saved && options.some((o) => o.id === saved) ? saved : fallback);
      })
      .catch(() => {}); // API down: keep "Auto"; Analyze will show the error
  }, []);

  function chooseProvider(id: string) {
    setProvider(id);
    try {
      localStorage.setItem(PROVIDER_KEY, id);
    } catch {}
  }

  const providerLabel = providers.find((o) => o.id === provider)?.label ?? provider;

  async function run() {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    try {
      setResult(await analyze(text, provider));
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
          maxLength={MAX_CHARS}
          className="w-full rounded-lg border border-zinc-300 bg-transparent p-3 dark:border-zinc-700"
          aria-label="Message to analyze"
        />
        <label className="flex flex-wrap items-center gap-2 text-sm text-zinc-600 dark:text-zinc-400">
          Model
          <select
            value={provider}
            onChange={(e) => chooseProvider(e.target.value)}
            className="rounded-lg border border-zinc-300 bg-transparent px-2 py-1 dark:border-zinc-700 dark:bg-zinc-900"
          >
            {providers.map((o) => (
              <option key={o.id} value={o.id}>
                {o.vendor ? `${o.label} · ${o.vendor}` : o.label}
              </option>
            ))}
          </select>
        </label>
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
        <p className="text-xs text-zinc-400">
          Messages are sent to Google Gemini / Groq free tiers, which may review them. Don&apos;t paste
          private chats.
        </p>
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
            <div className="flex flex-col gap-3 rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
              <div>
                <p className="text-sm text-zinc-500">What it means</p>
                <p>{result.meaning.en}</p>
              </div>
              <div>
                <p className="text-sm text-zinc-500">A reply in your own mix</p>
                <p className="font-medium">{result.meaning.reply}</p>
              </div>
              <p className="text-xs text-zinc-400">
                {result.meaning.provider} ·{" "}
                {result.meaning.register_kept
                  ? "our language ID confirmed the reply keeps your language mix"
                  : "the model fell back to English"}
              </p>
            </div>
          ) : (
            <p className="text-sm text-zinc-500">
              {provider === AUTO_OPTION.id
                ? "Meaning unavailable right now (no model configured, or all are busy)."
                : `No answer from ${providerLabel} right now (busy or rate-limited). Try Auto.`}
            </p>
          )}

          <p className="text-xs text-zinc-400">
            Language ID: {result.lid_source === "model" ? "trained model" : "rules baseline"}
          </p>
        </section>
      )}
    </main>
  );
}
