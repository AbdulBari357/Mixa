// API contract. Keep in sync with api/src/mixa/schemas.py.

export type Lang = "en" | "hi-ur" | "ar" | "ne" | "other";

export interface Token {
  text: string;
  start: number;
  end: number;
  lang: Lang;
  conf: number;
  /** Sound key: spellings that sound alike share it (bahut, bohot, bht -> "bt"). */
  key: string | null;
  /** e.g. { deva: "भाई", urdu: "بھائی", arabic: "بعد" } */
  scripts: Record<string, string>;
}

export interface Stats {
  languages: Lang[];
  switch_points: number;
  /** Code-Mixing Index, 0 = monolingual. */
  cmi: number;
}

export interface MeaningResult {
  /** What the message means, in plain English. */
  en: string;
  /** A short reply written the way the sender writes (same language mix). */
  reply: string;
  /** Model that answered, e.g. "gemini-3.1-flash-lite". */
  provider: string;
  /** Our own language ID confirmed the reply keeps the sender's language mix. */
  register_kept: boolean;
}

export interface ProviderOption {
  /** "auto" (fallback chain) or a model id, e.g. "gemini-3.5-flash-lite". */
  id: string;
  label: string;
  /** e.g. "Google Gemini", "Groq"; empty for auto. */
  vendor: string;
}

export interface ProvidersResponse {
  default: string;
  options: ProviderOption[];
}

export interface AnalyzeResponse {
  tokens: Token[];
  stats: Stats;
  meaning: MeaningResult | null;
  lid_source: "model" | "rules";
}
