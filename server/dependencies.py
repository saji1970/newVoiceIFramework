from __future__ import annotations

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from server.config import settings
from server.core.engine import CoreEngine
from server.providers.registry import provider_registry

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(api_key_header)) -> str:
    if settings.api_key == "changeme":
        return "dev"
    if not api_key or api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return api_key


_engine: CoreEngine | None = None


async def get_engine() -> CoreEngine:
    global _engine
    if _engine is None:
        _engine = CoreEngine(provider_registry=provider_registry)
    return _engine
