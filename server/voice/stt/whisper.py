from __future__ import annotations

import io
import logging

from server.config import settings
from server.voice.stt.base import STTProvider

logger = logging.getLogger(__name__)


class WhisperSTT(STTProvider):
    """OpenAI Whisper STT - supports both API and local model."""

    name = "whisper"

    def __init__(self, use_api: bool = True):
        self.use_api = use_api
        self._local_model = None

    def is_available(self) -> bool:
        if self.use_api:
            return bool(settings.openai_api_key)
        return True  # Local Whisper always available if installed

    async def transcribe(self, audio_data: bytes, format: str = "wav", language: str = "en") -> str:
        if self.use_api:
            return await self._transcribe_api(audio_data, format, language)
        return await self._transcribe_local(audio_data, format, language)

    async def _transcribe_api(self, audio_data: bytes, format: str, language: str) -> str:
        import openai

        client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

        audio_file = io.BytesIO(audio_data)
        audio_file.name = f"audio.{format}"

        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language,
        )
        return response.text

    async def _transcribe_local(self, audio_data: bytes, format: str, language: str) -> str:
        import asyncio

        def _run():
            import os
            import tempfile

            import whisper

            if self._local_model is None:
                self._local_model = whisper.load_model("base")

            with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as f:
                f.write(audio_data)
                tmp_path = f.name

            try:
                result = self._local_model.transcribe(tmp_path, language=language)
                return result["text"]
            finally:
                os.unlink(tmp_path)

        return await asyncio.get_event_loop().run_in_executor(None, _run)
