FROM python:3.12-slim AS base
COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project --no-dev
COPY src ./src
COPY models ./models

# Local development: all dependency groups (tests, ML training), auto-reload.
FROM base AS dev
RUN uv sync --frozen --all-groups
CMD ["uvicorn", "mixa.server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Deployment (default target). Hugging Face Spaces expects port 7860.
FROM base AS prod
RUN uv sync --frozen --no-dev
ENV PORT=7860
EXPOSE 7860
CMD ["sh", "-c", "uvicorn mixa.server:app --host 0.0.0.0 --port ${PORT}"]
