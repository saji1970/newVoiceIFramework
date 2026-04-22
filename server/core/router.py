from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from server.config import settings

if TYPE_CHECKING:
    from server.providers.base import LLMProvider
    from server.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)


class ProviderRouter:
    """Routes requests to the appropriate LLM provider based on config or request params."""

    def __init__(self, registry: ProviderRegistry):
        self.registry = registry

    def resolve(
        self,
        provider_name: str | None = None,
        model: str | None = None,
    ) -> tuple[LLMProvider, str]:
        """Resolve a provider instance and model name.

        Returns (provider, model_name).
        """
        name = provider_name or settings.default_llm_provider
        model_name = model or settings.default_llm_model

        provider = self.registry.get(name)
        if provider is None:
            available = self.registry.list_available()
            raise ValueError(
                f"Provider '{name}' not found. Available: {available}"
            )

        return provider, model_name
