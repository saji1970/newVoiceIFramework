from __future__ import annotations

import logging
from typing import AsyncIterator

import httpx

from server.config import settings
from server.voice.tts.base import TTSProvider

logger = logging.getLogger(__name__)


class ElevenLabsTTS(TTSProvider):
    """ElevenLabs Text-to-Speech."""

    name = "elevenlabs"
    BASE_URL = "https://api.elevenlabs.io/v1"

    def is_available(self) -> bool:
        return bool(settings.elevenlabs_api_key)

    def list_voices(self) -> list[str]:
        return ["rachel", "domi", "bella", "antoni", "elli", "josh", "arnold", "adam", "sam"]

    def _headers(self) -> dict:
        return {
            "xi-api-key": settings.elevenlabs_api_key,
            "Content-Type": "application/json",
        }

    async def synthesize(self, text: str, voice: str = "rachel", **kwargs) -> bytes:
        voice_id = kwargs.get("voice_id", voice)
        model_id = kwargs.get("model_id", "eleven_multilingual_v2")

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.BASE_URL}/text-to-speech/{voice_id}",
                headers=self._headers(),
                json={
                    "text": text,
                    "model_id": model_id,
                    "voice_settings": {
                        "stability": kwargs.get("stability", 0.5),
                        "similarity_boost": kwargs.get("similarity_boost", 0.75),
                    },
                },
            )
            response.raise_for_status()
            return response.content

    async def stream_synthesize(
        self, text: str, voice: str = "rachel", **kwargs
    ) -> AsyncIterator[bytes]:
        voice_id = kwargs.get("voice_id", voice)
        model_id = kwargs.get("model_id", "eleven_multilingual_v2")

        async with httpx.AsyncClient(timeout=30) as client:
            async with client.stream(
                "POST",
                f"{self.BASE_URL}/text-to-speech/{voice_id}/stream",
                headers=self._headers(),
                json={
                    "text": text,
                    "model_id": model_id,
                    "voice_settings": {
                        "stability": kwargs.get("stability", 0.5),
                        "similarity_boost": kwargs.get("similarity_boost", 0.75),
                    },
                },
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes(chunk_size=4096):
                    yield chunk
