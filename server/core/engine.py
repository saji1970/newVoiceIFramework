from __future__ import annotations

import logging
from typing import AsyncIterator

from server.core.conversation import Conversation, ConversationManager
from server.core.memory import MemoryStore
from server.core.router import ProviderRouter
from server.providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)


class CoreEngine:
    """Main orchestrator: routes chat requests through providers, manages conversations."""

    def __init__(self, provider_registry: ProviderRegistry):
        self.router = ProviderRouter(provider_registry)
        self.conversations = ConversationManager()
        self.memory = MemoryStore()

    async def chat(
        self,
        message: str,
        conversation_id: str | None = None,
        system_prompt: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> tuple[str, Conversation]:
        """Send a chat message and get a full response."""
        conv = self.conversations.get_or_create(conversation_id, system_prompt)
        conv.add_message("user", message)

        llm, model_name = self.router.resolve(provider, model)
        messages = conv.to_provider_messages()

        response = await llm.chat(
            messages=messages,
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        conv.add_message("assistant", response)
        return response, conv

    async def chat_stream(
        self,
        message: str,
        conversation_id: str | None = None,
        system_prompt: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> tuple[AsyncIterator[str], Conversation]:
        """Send a chat message and get a streaming response."""
        conv = self.conversations.get_or_create(conversation_id, system_prompt)
        conv.add_message("user", message)

        llm, model_name = self.router.resolve(provider, model)
        messages = conv.to_provider_messages()

        collected: list[str] = []

        async def stream_and_collect():
            async for chunk in llm.stream(
                messages=messages,
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            ):
                collected.append(chunk)
                yield chunk
            # After streaming completes, save the full response
            conv.add_message("assistant", "".join(collected))

        return stream_and_collect(), conv
