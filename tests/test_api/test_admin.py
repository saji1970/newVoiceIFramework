from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "VoiceI Framework"
    assert "version" in data
    assert data.get("docs") == "/docs"


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "uptime_seconds" in data
    assert "version" in data


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
