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

export interface Meaning {
  en: string;
  same_register: string;
}

export interface AnalyzeResponse {
  tokens: Token[];
  stats: Stats;
  meaning: Meaning | null;
  lid_source: "model" | "rules";
}
