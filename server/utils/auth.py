from __future__ import annotations

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from server.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(api_key: str | None = Security(api_key_header)) -> str:
    """Dependency that enforces API key authentication.

    If API_KEY is set to 'changeme' (default), auth is disabled for dev mode.
    """
    if settings.api_key == "changeme":
        return "dev-mode"
    if not api_key or api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Provide X-API-Key header.",
        )
    return api_key
