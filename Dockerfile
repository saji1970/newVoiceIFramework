# ── Stage 1: Build dashboard ──
FROM node:22-alpine AS dashboard-build

WORKDIR /dashboard
COPY dashboard/package.json dashboard/package-lock.json ./
RUN npm ci
COPY dashboard/ .
RUN npm run build

# ── Stage 2: Python API + static dashboard ──
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python package
COPY pyproject.toml README.md ./
COPY server ./server
COPY pipelines ./pipelines

RUN pip install --upgrade pip && pip install -e .

# Copy built dashboard into location the server will serve
COPY --from=dashboard-build /dashboard/dist ./dashboard_dist

ENV HOST=0.0.0.0 \
    PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "uvicorn server.main:app --host ${HOST} --port ${PORT}"]
