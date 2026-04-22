from __future__ import annotations

from typing import AsyncIterator

from server.config import settings
from server.providers.base import LLMProvider


class MistralProvider(LLMProvider):
    """Mistral AI provider."""

    name = "mistral"

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from mistralai import Mistral
            self._client = Mistral(api_key=settings.mistral_api_key)
        return self._client

    def is_available(self) -> bool:
        return bool(settings.mistral_api_key)

    def list_models(self) -> list[str]:
        return ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest", "open-mistral-nemo"]

    async def chat(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> str:
        response = await self.client.chat.complete_async(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    async def stream(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> AsyncIterator[str]:
        response = await self.client.chat.stream_async(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        async for chunk in response:
            delta = chunk.data.choices[0].delta
            if delta.content:
                yield delta.content
