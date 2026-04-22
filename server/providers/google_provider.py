from __future__ import annotations

from typing import AsyncIterator

from server.config import settings
from server.providers.base import LLMProvider


class GoogleProvider(LLMProvider):
    """Google Gemini provider."""

    name = "google"

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=settings.google_api_key)
        return self._client

    def is_available(self) -> bool:
        return bool(settings.google_api_key)

    def list_models(self) -> list[str]:
        return ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]

    async def chat(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> str:
        client = self._get_client()

        # Convert messages to Gemini format
        system_instruction = None
        contents = []
        for m in messages:
            if m["role"] == "system":
                system_instruction = m["content"]
            else:
                role = "user" if m["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": m["content"]}]})

        from google.genai import types
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system_instruction,
        )

        response = await client.aio.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )
        return response.text or ""

    async def stream(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> AsyncIterator[str]:
        client = self._get_client()

        system_instruction = None
        contents = []
        for m in messages:
            if m["role"] == "system":
                system_instruction = m["content"]
            else:
                role = "user" if m["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": m["content"]}]})

        from google.genai import types
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system_instruction,
        )

        async for chunk in await client.aio.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
        ):
            if chunk.text:
                yield chunk.text
