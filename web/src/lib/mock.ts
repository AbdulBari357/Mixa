import type { AnalyzeResponse } from "./types";

// Hand-written example matching the API contract, for UI work without the backend.
export const MOCK_ANALYSIS: AnalyzeResponse = {
  tokens: [
    { text: "bhai", start: 0, end: 4, lang: "hi-ur", conf: 0.97, key: "bE", scripts: { deva: "भाई", urdu: "بھائی" } },
    { text: "kal", start: 5, end: 8, lang: "hi-ur", conf: 0.93, key: "kl", scripts: { deva: "कल", urdu: "کل" } },
    { text: "meeting", start: 9, end: 16, lang: "en", conf: 0.99, key: "mtng", scripts: {} },
    { text: "hai", start: 17, end: 20, lang: "hi-ur", conf: 0.95, key: "hE", scripts: { deva: "है", urdu: "ہے" } },
    { text: ",", start: 20, end: 21, lang: "other", conf: 1, key: null, scripts: {} },
    { text: "ana", start: 22, end: 25, lang: "ar", conf: 0.88, key: "anA", scripts: { arabic: "أنا" } },
    { text: "coming", start: 26, end: 32, lang: "en", conf: 0.99, key: "kmng", scripts: {} },
    { text: "ba3d", start: 33, end: 37, lang: "ar", conf: 0.91, key: "bd", scripts: { arabic: "بعد" } },
    { text: "shwaya", start: 38, end: 44, lang: "ar", conf: 0.86, key: "svA", scripts: { arabic: "شوية" } },
    { text: ",", start: 44, end: 45, lang: "other", conf: 1, key: null, scripts: {} },
    { text: "traffic", start: 46, end: 53, lang: "en", conf: 0.99, key: "trfk", scripts: {} },
    { text: "bohot", start: 54, end: 59, lang: "hi-ur", conf: 0.96, key: "bt", scripts: { deva: "बहुत", urdu: "بہت" } },
    { text: "hai", start: 60, end: 63, lang: "hi-ur", conf: 0.95, key: "hE", scripts: { deva: "है", urdu: "ہے" } },
  ],
  stats: { languages: ["hi-ur", "en", "ar"], switch_points: 7, cmi: 54.5 },
  meaning: {
    en: "Bro, is the meeting tomorrow? I'm coming in a little while, there's a lot of traffic.",
    same_register: "Bhai meeting kal hai na? Ana coming ba3d shwaya, traffic bohot zyada hai.",
  },
  lid_source: "rules",
};
