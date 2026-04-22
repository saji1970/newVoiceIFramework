from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "uptime_seconds" in data
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_config(client):
    response = await client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert "default_provider" in data
    assert "default_model" in data


@pytest.mark.asyncio
async def test_providers_status(client):
    response = await client.get("/api/providers/status")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert "available" in data
