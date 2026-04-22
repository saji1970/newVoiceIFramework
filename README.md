# VoiceI Framework

A full-stack **LLM interface framework**: FastAPI backend, React dashboard (chat, voice, pipelines, flow builder), optional TypeScript SDK, and YAML-defined pipelines. Use it to prototype or ship assistants with multiple model providers and voice (STT/TTS) integrations.

## Features

- **Chat** — Streaming and non-streaming LLM calls with conversation persistence
- **Providers** — OpenAI, Anthropic, Ollama, vLLM, and more (pluggable registry)
- **Pipelines** — Visual flow builder and YAML examples for multi-step logic
- **Voice** — STT/TTS abstractions (Whisper, Deepgram, OpenAI, ElevenLabs, etc.) when optional deps are installed
- **API** — OpenAPI at [`/docs`](http://localhost:8000/docs); health at `GET /api/health`
- **Security** — `X-API-Key` when `API_KEY` is set to a non-default value in production

## Requirements

- **Python** 3.11+ (3.12 recommended)
- **Node** 20+ (for the dashboard)
- **Optional:** Docker + Docker Compose

## Quick start (local)

1. **Backend**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -e ".[dev,voice,all-providers]"
   copy .env.example .env
   # Edit .env: set at least one LLM key (e.g. OPENAI_API_KEY) and API_KEY for non-dev auth
   make dev
   ```

2. **Dashboard** (separate terminal)

   ```bash
   cd dashboard
   npm install
   npm run dev
   ```

   Open [http://127.0.0.1:5173](http://127.0.0.1:5173). The Vite dev server proxies `/api` to the backend (see `dashboard/vite.config.ts`).

3. **When `API_KEY` is not `changeme`**

   Set the same value in the dashboard build env:

   ```bash
   set VITE_API_KEY=your-key
   npm run dev
   ```

   (Use `VITE_API_KEY` in `.env` under `dashboard/` for local development.)

## Docker Compose

```bash
copy .env.example .env
# Configure API keys and DATABASE_URL as needed
docker compose up -d --build
```

- API: [http://localhost:8000](http://localhost:8000) — root `GET /` returns service JSON; interactive docs at `/docs`
- Dashboard: [http://localhost:5173](http://localhost:5173)  
  The dashboard service sets `API_PROXY_TARGET=http://server:8000` so the Vite proxy can reach the API container.

## Project layout

| Path | Purpose |
|------|--------|
| `server/` | FastAPI app, engine, providers, storage, voice |
| `dashboard/` | Vite + React + Tailwind UI |
| `sdk/` | TypeScript client / embeddable pieces |
| `pipelines/` | Example YAML pipeline definitions |
| `tests/` | Pytest (API, providers) |

## Commands (Makefile)

| Target | Action |
|--------|--------|
| `make install` | Editable install with dev + voice + all provider extras |
| `make dev` | Run Uvicorn with reload |
| `make test` | `pytest` |
| `make lint` / `make format` | Ruff |
| `make db-init` | Create DB tables (SQLAlchemy) |
| `make docker-up` / `make docker-down` | Compose up/down |

## API notes

- **OpenAPI** — [http://localhost:8000/docs](http://localhost:8000/docs) when the server is running
- **Root** — `GET /` returns service name, version, and links
- **Provider list** — `GET /api/providers` lists LLM backends; `GET /api/providers/status` (admin) reports registry availability (must not conflict with a provider named `status`—routers are ordered so this path resolves correctly)

## License

MIT — see [LICENSE](LICENSE).
