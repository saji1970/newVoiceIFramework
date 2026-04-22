from __future__ import annotations

from typing import AsyncIterator

import anthropic

from server.config import settings
from server.providers.base import LLMProvider


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self):
        self._client: anthropic.AsyncAnthropic | None = None

    @property
    def client(self) -> anthropic.AsyncAnthropic:
        if self._client is None:
            self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        return self._client

    def is_available(self) -> bool:
        return bool(settings.anthropic_api_key)

    def list_models(self) -> list[str]:
        return [
            "claude-opus-4-6",
            "claude-sonnet-4-5-20250929",
            "claude-haiku-4-5-20251001",
            "claude-3-5-sonnet-20241022",
        ]

    async def chat(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> str:
        system_prompt = None
        filtered = []
        for m in messages:
            if m["role"] == "system":
                system_prompt = m["content"]
            else:
                filtered.append(m)

        create_kwargs = dict(
            model=model,
            messages=filtered,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )
        if system_prompt:
            create_kwargs["system"] = system_prompt

        response = await self.client.messages.create(**create_kwargs)
        return response.content[0].text

    async def stream(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> AsyncIterator[str]:
        system_prompt = None
        filtered = []
        for m in messages:
            if m["role"] == "system":
                system_prompt = m["content"]
            else:
                filtered.append(m)

        create_kwargs = dict(
            model=model,
            messages=filtered,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )
        if system_prompt:
            create_kwargs["system"] = system_prompt

        async with self.client.messages.stream(**create_kwargs) as stream:
            async for text in stream.text_stream:
                yield text
