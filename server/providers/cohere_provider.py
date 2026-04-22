from __future__ import annotations

from typing import AsyncIterator

from server.config import settings
from server.providers.base import LLMProvider


class CohereProvider(LLMProvider):
    """Cohere provider."""

    name = "cohere"

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            import cohere
            self._client = cohere.AsyncClientV2(api_key=settings.cohere_api_key)
        return self._client

    def is_available(self) -> bool:
        return bool(settings.cohere_api_key)

    def list_models(self) -> list[str]:
        return ["command-r-plus", "command-r", "command-light"]

    async def chat(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> str:
        response = await self.client.chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.message.content[0].text

    async def stream(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> AsyncIterator[str]:
        async for event in self.client.chat_stream(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            if event.type == "content-delta":
                yield event.delta.message.content.text
