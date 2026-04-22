from __future__ import annotations

import pytest

from server.providers.base import LLMProvider
from server.providers.registry import ProviderRegistry


class MockProvider(LLMProvider):
    name = "mock"

    async def chat(self, messages, model, **kwargs):
        return "mock response"

    async def stream(self, messages, model, **kwargs):
        yield "mock "
        yield "stream"

    def is_available(self):
        return True

    def list_models(self):
        return ["mock-model"]


class UnavailableProvider(LLMProvider):
    name = "unavailable"

    async def chat(self, messages, model, **kwargs):
        return ""

    async def stream(self, messages, model, **kwargs):
        yield ""

    def is_available(self):
        return False


def test_register_and_get():
    registry = ProviderRegistry()
    provider = MockProvider()
    registry.register(provider)
    assert registry.get("mock") is provider
    assert registry.get("nonexistent") is None


def test_list_available():
    registry = ProviderRegistry()
    registry.register(MockProvider())
    registry.register(UnavailableProvider())
    available = registry.list_available()
    assert "mock" in available
    assert "unavailable" not in available


def test_list_all():
    registry = ProviderRegistry()
    registry.register(MockProvider())
    registry.register(UnavailableProvider())
    all_providers = registry.list_all()
    assert all_providers == {"mock": True, "unavailable": False}


@pytest.mark.asyncio
async def test_mock_provider_chat():
    p = MockProvider()
    result = await p.chat(messages=[{"role": "user", "content": "hi"}], model="mock-model")
    assert result == "mock response"


@pytest.mark.asyncio
async def test_mock_provider_stream():
    p = MockProvider()
    chunks = []
    async for chunk in p.stream(messages=[{"role": "user", "content": "hi"}], model="mock-model"):
        chunks.append(chunk)
    assert "".join(chunks) == "mock stream"
