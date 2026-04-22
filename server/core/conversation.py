from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class Message:
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict | None = None


@dataclass
class Conversation:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    messages: list[Message] = field(default_factory=list)
    system_prompt: str | None = None
    metadata: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def add_message(self, role: str, content: str, **kwargs) -> Message:
        msg = Message(role=role, content=content, **kwargs)
        self.messages.append(msg)
        return msg

    def to_provider_messages(self) -> list[dict]:
        """Convert to the list-of-dicts format expected by LLM providers."""
        msgs = []
        if self.system_prompt:
            msgs.append({"role": "system", "content": self.system_prompt})
        for m in self.messages:
            msgs.append({"role": m.role, "content": m.content})
        return msgs

    def trim(self, max_messages: int = 50):
        """Keep only the most recent messages."""
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]


class ConversationManager:
    """In-memory conversation store (backed by DB for persistence)."""

    def __init__(self):
        self._conversations: dict[str, Conversation] = {}

    def create(self, system_prompt: str | None = None, **kwargs) -> Conversation:
        conv = Conversation(system_prompt=system_prompt, **kwargs)
        self._conversations[conv.id] = conv
        return conv

    def get(self, conversation_id: str) -> Conversation | None:
        return self._conversations.get(conversation_id)

    def get_or_create(
        self, conversation_id: str | None = None, system_prompt: str | None = None
    ) -> Conversation:
        if conversation_id and conversation_id in self._conversations:
            return self._conversations[conversation_id]
        return self.create(system_prompt=system_prompt)

    def delete(self, conversation_id: str) -> bool:
        return self._conversations.pop(conversation_id, None) is not None

    def list_ids(self) -> list[str]:
        return list(self._conversations.keys())
