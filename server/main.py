from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.config import settings
from server.storage.database import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
    logger.info("Starting VoiceI Framework server")

    if settings.api_key == "changeme":
        logger.warning("=" * 60)
        logger.warning("RUNNING WITH DEFAULT API KEY - AUTH IS DISABLED")
        logger.warning("Set API_KEY environment variable for production use")
        logger.warning("=" * 60)

    await init_db()

    from server.providers.registry import provider_registry
    await provider_registry.discover()
    logger.info("Provider registry initialized")

    from server.voice.manager import voice_manager
    try:
        await voice_manager.initialize()
        logger.info("Voice manager initialized")
    except Exception as e:
        logger.warning(f"Voice manager initialization failed (voice features unavailable): {e}")

    yield
    logger.info("Shutting down VoiceI Framework server")


app = FastAPI(
    title="VoiceI Framework",
    description="LLM-powered interface framework with AI chat, voice, and visual pipeline builder",
    version="0.1.0",
    lifespan=lifespan,
)

_cors_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
from server.api.chat import router as chat_router
from server.api.admin import router as admin_router
from server.api.pipelines import router as pipelines_router
from server.api.providers import router as providers_router
from server.api.connectors import router as connectors_router
from server.api.voice import router as voice_router

app.include_router(chat_router, prefix="/api")
app.include_router(voice_router, prefix="/api")
app.include_router(pipelines_router, prefix="/api")
app.include_router(providers_router, prefix="/api")
app.include_router(connectors_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
