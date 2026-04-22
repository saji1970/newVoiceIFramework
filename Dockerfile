# VoiceI Framework API
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install package (declared dependencies only; use docker-compose build args for extras)
COPY pyproject.toml README.md ./
COPY server ./server
COPY pipelines ./pipelines

RUN pip install --upgrade pip && pip install -e .

ENV DATABASE_URL=sqlite+aiosqlite:///./data/voicei.db \
    PIPLINES_DIR=pipelines \
    HOST=0.0.0.0 \
    PORT=8000

RUN mkdir -p /app/data

EXPOSE 8000

CMD ["sh", "-c", "uvicorn server.main:app --host ${HOST} --port ${PORT}"]
