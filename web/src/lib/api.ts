import { MOCK_ANALYSIS } from "./mock";
import type { AnalyzeResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "1";

export async function analyze(text: string): Promise<AnalyzeResponse> {
  if (USE_MOCK) return MOCK_ANALYSIS;
  const res = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
