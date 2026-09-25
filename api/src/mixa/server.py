import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mixa.config import get_settings
from mixa.pipeline import analyze
from mixa.pipeline.lid import model_available
from mixa.schemas import AnalyzeRequest, AnalyzeResponse

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Mixa API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "lid_model": model_available(),
        "gemini": bool(get_settings().gemini_api_key),
    }


@app.post("/analyze")
def analyze_text(req: AnalyzeRequest) -> AnalyzeResponse:
    return analyze(req.text)
