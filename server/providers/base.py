from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator


class LLMProvider(ABC):
    """Abstract base class for all LLM provider adapters."""

    name: str = "base"

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> str:
        """Send messages and return a complete response string."""

    @abstractmethod
    async def stream(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Send messages and yield response chunks as they arrive."""

    async def embeddings(self, texts: list[str], model: str, **kwargs) -> list[list[float]]:
        """Generate embeddings. Override in providers that support it."""
        raise NotImplementedError(f"{self.name} does not support embeddings")

    def is_available(self) -> bool:
        """Check if this provider is configured and available."""
        return True

    def list_models(self) -> list[str]:
        """Return a list of known model IDs for this provider."""
        return []
