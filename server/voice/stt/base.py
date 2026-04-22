from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator


class STTProvider(ABC):
    """Abstract base class for speech-to-text providers."""

    name: str = "base"

    @abstractmethod
    async def transcribe(self, audio_data: bytes, format: str = "wav", language: str = "en") -> str:
        """Transcribe an audio buffer to text (batch mode)."""

    async def stream_transcribe(
        self, audio_stream: AsyncIterator[bytes], format: str = "wav", language: str = "en"
    ) -> AsyncIterator[str]:
        """Stream transcribe audio chunks to text. Override for real-time providers."""
        raise NotImplementedError(f"{self.name} does not support streaming STT")

    def is_available(self) -> bool:
        return True
