import { MOCK_ANALYSIS, MOCK_PROVIDERS } from "./mock";
import type { AnalyzeResponse, ProvidersResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "1";

export async function getProviders(): Promise<ProvidersResponse> {
  if (USE_MOCK) return MOCK_PROVIDERS;
  const res = await fetch(`${API_URL}/providers`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

/** provider: "auto" for the fallback chain, or a model id from getProviders(). */
export async function analyze(text: string, provider = "auto"): Promise<AnalyzeResponse> {
  if (USE_MOCK) return MOCK_ANALYSIS;
  const res = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, provider }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
