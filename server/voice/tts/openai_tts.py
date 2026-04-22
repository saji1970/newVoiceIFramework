from __future__ import annotations

import logging
from typing import AsyncIterator

import openai

from server.config import settings
from server.voice.tts.base import TTSProvider

logger = logging.getLogger(__name__)


class OpenAITTS(TTSProvider):
    """OpenAI Text-to-Speech."""

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

    def list_voices(self) -> list[str]:
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    async def synthesize(self, text: str, voice: str = "alloy", **kwargs) -> bytes:
        model = kwargs.get("model", settings.default_tts_model)
        response = await self.client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format=kwargs.get("format", "mp3"),
        )
        return response.content

    async def stream_synthesize(
        self, text: str, voice: str = "alloy", **kwargs
    ) -> AsyncIterator[bytes]:
        model = kwargs.get("model", settings.default_tts_model)
        response = await self.client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format=kwargs.get("format", "mp3"),
        )
        # OpenAI TTS returns full audio; chunk it for streaming
        content = response.content
        chunk_size = 4096
        for i in range(0, len(content), chunk_size):
            yield content[i : i + chunk_size]
