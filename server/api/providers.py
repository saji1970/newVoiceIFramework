from __future__ import annotations

from fastapi import APIRouter, Depends

from server.dependencies import verify_api_key
from server.providers.registry import provider_registry

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("")
async def list_providers(_api_key: str = Depends(verify_api_key)):
    """List all registered providers and their status."""
    providers = []
    for name, available in provider_registry.list_all().items():
        p = provider_registry.get(name)
        providers.append(
            {
                "name": name,
                "available": available,
                "models": p.list_models() if p else [],
            }
        )
    return {"providers": providers}


@router.get("/{provider_name}")
async def get_provider(provider_name: str, _api_key: str = Depends(verify_api_key)):
    """Get details for a specific provider."""
    p = provider_registry.get(provider_name)
    if p is None:
        from fastapi import HTTPException

        raise HTTPException(404, f"Provider '{provider_name}' not found")
    return {
        "name": p.name,
        "available": p.is_available(),
        "models": p.list_models(),
    }


@router.get("/{provider_name}/models")
async def list_models(provider_name: str, _api_key: str = Depends(verify_api_key)):
    """List available models for a provider."""
    p = provider_registry.get(provider_name)
    if p is None:
        from fastapi import HTTPException

        raise HTTPException(404, f"Provider '{provider_name}' not found")
    return {"models": p.list_models()}
