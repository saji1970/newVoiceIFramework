from __future__ import annotations

from typing import AsyncIterator

import openai

from server.config import settings
from server.providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self):
        self._client: openai.AsyncOpenAI | None = None

    @property
    def client(self) -> openai.AsyncOpenAI:
        if self._client is None:
            self._client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        return self._client

    def is_available(self) -> bool:
        return bool(settings.openai_api_key)

    def list_models(self) -> list[str]:
        return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "o1", "o1-mini"]

    async def chat(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> str:
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
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
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

    async def embeddings(self, texts: list[str], model: str = "text-embedding-3-small", **kwargs) -> list[list[float]]:
        response = await self.client.embeddings.create(
            model=model,
            input=texts,
            **kwargs,
        )
        return [item.embedding for item in response.data]
