from __future__ import annotations

from typing import AsyncIterator

import openai

from server.config import settings
from server.providers.base import LLMProvider


class VLLMProvider(LLMProvider):
    """vLLM / LM Studio provider (OpenAI-compatible API)."""

    name = "vllm"

    def __init__(self):
        self._client: openai.AsyncOpenAI | None = None

    @property
    def client(self) -> openai.AsyncOpenAI:
        if self._client is None:
            self._client = openai.AsyncOpenAI(
                base_url=settings.vllm_base_url,
                api_key=settings.vllm_api_key or "not-needed",
            )
        return self._client

    def is_available(self) -> bool:
        return bool(settings.vllm_base_url)

    def list_models(self) -> list[str]:
        # Models are dynamic, depends on what's loaded
        return []

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
