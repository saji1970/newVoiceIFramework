from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncIterator

import websockets

from server.config import settings
from server.voice.stt.base import STTProvider

logger = logging.getLogger(__name__)


class DeepgramSTT(STTProvider):
    """Deepgram real-time STT via WebSocket."""

    name = "deepgram"

    def is_available(self) -> bool:
        return bool(settings.deepgram_api_key)

    async def transcribe(self, audio_data: bytes, format: str = "wav", language: str = "en") -> str:
        """Batch transcription via Deepgram REST API."""
        import httpx

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.deepgram.com/v1/listen",
                headers={
                    "Authorization": f"Token {settings.deepgram_api_key}",
                    "Content-Type": f"audio/{format}",
                },
                params={"model": "nova-2", "language": language},
                content=audio_data,
            )
            response.raise_for_status()
            data = response.json()
            return data["results"]["channels"][0]["alternatives"][0]["transcript"]

    async def stream_transcribe(
        self, audio_stream: AsyncIterator[bytes], format: str = "wav", language: str = "en"
    ) -> AsyncIterator[str]:
        """Real-time streaming transcription via Deepgram WebSocket."""
        url = (
            f"wss://api.deepgram.com/v1/listen"
            f"?model=nova-2&language={language}&encoding=linear16&sample_rate=16000"
        )
        headers = {"Authorization": f"Token {settings.deepgram_api_key}"}

        async with websockets.connect(url, extra_headers=headers) as ws:
            # Task to send audio chunks
            async def send_audio():
                async for chunk in audio_stream:
                    await ws.send(chunk)
                # Signal end of audio
                await ws.send(json.dumps({"type": "CloseStream"}))

            send_task = asyncio.create_task(send_audio())

            try:
                async for msg in ws:
                    data = json.loads(msg)
                    if data.get("type") == "Results":
                        transcript = (
                            data.get("channel", {})
                            .get("alternatives", [{}])[0]
                            .get("transcript", "")
                        )
                        if transcript and data.get("is_final"):
                            yield transcript
            finally:
                send_task.cancel()
