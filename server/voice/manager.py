from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field

from server.config import settings
from server.voice.stt.base import STTProvider
from server.voice.tts.base import TTSProvider

logger = logging.getLogger(__name__)


@dataclass
class VoiceSession:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    stt_provider: str = ""
    tts_provider: str = ""
    tts_voice: str = ""
    conversation_id: str | None = None
    active: bool = True


class VoiceManager:
    """Orchestrates voice sessions, STT/TTS provider selection."""

    def __init__(self):
        self._sessions: dict[str, VoiceSession] = {}
        self._stt_providers: dict[str, STTProvider] = {}
        self._tts_providers: dict[str, TTSProvider] = {}

    def register_stt(self, provider: STTProvider):
        if provider.is_available():
            self._stt_providers[provider.name] = provider
            logger.info(f"Registered STT provider: {provider.name}")

    def register_tts(self, provider: TTSProvider):
        if provider.is_available():
            self._tts_providers[provider.name] = provider
            logger.info(f"Registered TTS provider: {provider.name}")

    def get_stt(self, name: str | None = None) -> STTProvider:
        name = name or settings.default_stt_provider
        provider = self._stt_providers.get(name)
        if provider is None:
            available = list(self._stt_providers.keys())
            raise ValueError(f"STT provider '{name}' not found. Available: {available}")
        return provider

    def get_tts(self, name: str | None = None) -> TTSProvider:
        name = name or settings.default_tts_provider
        provider = self._tts_providers.get(name)
        if provider is None:
            available = list(self._tts_providers.keys())
            raise ValueError(f"TTS provider '{name}' not found. Available: {available}")
        return provider

    def create_session(self, **kwargs) -> VoiceSession:
        session = VoiceSession(
            stt_provider=kwargs.get("stt_provider", settings.default_stt_provider),
            tts_provider=kwargs.get("tts_provider", settings.default_tts_provider),
            tts_voice=kwargs.get("tts_voice", settings.default_tts_voice),
            conversation_id=kwargs.get("conversation_id"),
        )
        self._sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> VoiceSession | None:
        return self._sessions.get(session_id)

    def end_session(self, session_id: str):
        session = self._sessions.pop(session_id, None)
        if session:
            session.active = False

    async def initialize(self):
        """Auto-discover and register STT/TTS providers."""
        from server.voice.stt.deepgram import DeepgramSTT
        from server.voice.stt.whisper import WhisperSTT
        from server.voice.tts.elevenlabs import ElevenLabsTTS
        from server.voice.tts.openai_tts import OpenAITTS

        for cls in [WhisperSTT, DeepgramSTT]:
            try:
                self.register_stt(cls())
            except Exception as e:
                logger.debug(f"STT provider {cls.name} not available: {e}")

        for cls in [OpenAITTS, ElevenLabsTTS]:
            try:
                self.register_tts(cls())
            except Exception as e:
                logger.debug(f"TTS provider {cls.name} not available: {e}")


# Singleton
voice_manager = VoiceManager()
