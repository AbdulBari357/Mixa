import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from mixa.config import get_settings
from mixa.pipeline import analyze
from mixa.pipeline.lid import model_available
from mixa.pipeline.meaning import AUTO, provider_names, provider_options, recent_failures
from mixa.schemas import AnalyzeRequest, AnalyzeResponse, ProvidersResponse

logging.basicConfig(level=logging.INFO)

# Build the providers at startup so a typo in MEANING_CHAIN fails the boot, not every request.
provider_names()

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
        "meaning_providers": provider_names(),
        # Non-empty means a model is failing and the chain is silently falling back.
        "recent_failures": recent_failures(),
    }


@app.get("/providers")
def providers() -> ProvidersResponse:
    """LLMs the web app may choose between. Only configured ones (with an API key) appear."""
    return ProvidersResponse(default=AUTO, options=provider_options())


@app.post("/analyze")
def analyze_text(req: AnalyzeRequest) -> AnalyzeResponse:
    if req.provider not in {o.id for o in provider_options()}:
        raise HTTPException(status_code=422, detail=f"Unknown provider {req.provider!r}")
    return analyze(req.text, provider=req.provider)
