from __future__ import annotations

import time

from fastapi import APIRouter, Depends

from server.config import settings
from server.dependencies import verify_api_key
from server.providers.registry import provider_registry
from server.version import __version__

router = APIRouter(tags=["admin"])

_start_time = time.time()


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - _start_time, 1),
        "version": __version__,
    }


@router.get("/config")
async def get_config(_api_key: str = Depends(verify_api_key)):
    return {
        "default_provider": settings.default_llm_provider,
        "default_model": settings.default_llm_model,
        "default_stt_provider": settings.default_stt_provider,
        "default_tts_provider": settings.default_tts_provider,
        "debug": settings.debug,
    }


@router.get("/providers/status")
async def providers_status(_api_key: str = Depends(verify_api_key)):
    return {
        "providers": provider_registry.list_all(),
        "available": provider_registry.list_available(),
    }
