from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator


class TTSProvider(ABC):
    """Abstract base class for text-to-speech providers."""

    name: str = "base"

    @abstractmethod
    async def synthesize(self, text: str, voice: str = "default", **kwargs) -> bytes:
        """Synthesize text to audio bytes (batch mode)."""

    async def stream_synthesize(
        self, text: str, voice: str = "default", **kwargs
    ) -> AsyncIterator[bytes]:
        """Stream synthesize text to audio chunks. Override for streaming providers."""
        # Default: just return the full audio as a single chunk
        audio = await self.synthesize(text, voice, **kwargs)
        yield audio

    def is_available(self) -> bool:
        return True

    def list_voices(self) -> list[str]:
        return []
