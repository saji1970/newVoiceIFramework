from __future__ import annotations

import logging

from server.providers.base import LLMProvider

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Auto-discovery registry for LLM providers."""

    def __init__(self):
        self._providers: dict[str, LLMProvider] = {}

    def register(self, provider: LLMProvider):
        self._providers[provider.name] = provider
        logger.info(f"Registered provider: {provider.name}")

    def get(self, name: str) -> LLMProvider | None:
        return self._providers.get(name)

    def list_available(self) -> list[str]:
        return [name for name, p in self._providers.items() if p.is_available()]

    def list_all(self) -> dict[str, bool]:
        return {name: p.is_available() for name, p in self._providers.items()}

    async def discover(self):
        """Import and register all built-in providers."""
        from server.providers.anthropic_provider import AnthropicProvider
        from server.providers.ollama_provider import OllamaProvider
        from server.providers.openai_provider import OpenAIProvider

        for cls in [OpenAIProvider, AnthropicProvider, OllamaProvider]:
            try:
                provider = cls()
                if provider.is_available():
                    self.register(provider)
                else:
                    logger.debug(f"Provider {cls.name} not configured, skipping")
            except Exception as e:
                logger.warning(f"Failed to init provider {cls.name}: {e}")

        # Try optional providers
        try:
            from server.providers.google_provider import GoogleProvider

            p = GoogleProvider()
            if p.is_available():
                self.register(p)
        except ImportError:
            pass

        try:
            from server.providers.mistral_provider import MistralProvider

            p = MistralProvider()
            if p.is_available():
                self.register(p)
        except ImportError:
            pass

        try:
            from server.providers.cohere_provider import CohereProvider

            p = CohereProvider()
            if p.is_available():
                self.register(p)
        except ImportError:
            pass

        try:
            from server.providers.vllm_provider import VLLMProvider

            p = VLLMProvider()
            if p.is_available():
                self.register(p)
        except Exception:
            pass


# Singleton
provider_registry = ProviderRegistry()
