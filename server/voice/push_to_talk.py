from __future__ import annotations

import logging
from dataclasses import dataclass

from server.core.engine import CoreEngine
from server.voice.manager import VoiceManager

logger = logging.getLogger(__name__)


@dataclass
class PTTResult:
    transcript: str
    response: str
    audio: bytes | None = None
    conversation_id: str | None = None


class PushToTalkHandler:
    """Handles push-to-talk: receive audio → STT → LLM → TTS → return."""

    def __init__(self, engine: CoreEngine, voice_manager: VoiceManager):
        self.engine = engine
        self.voice_manager = voice_manager

    async def process(
        self,
        audio_data: bytes,
        audio_format: str = "wav",
        language: str = "en",
        stt_provider: str | None = None,
        tts_provider: str | None = None,
        tts_voice: str | None = None,
        llm_provider: str | None = None,
        llm_model: str | None = None,
        conversation_id: str | None = None,
        system_prompt: str | None = None,
    ) -> PTTResult:
        # 1. Speech-to-text
        stt = self.voice_manager.get_stt(stt_provider)
        transcript = await stt.transcribe(audio_data, format=audio_format, language=language)
        logger.info(f"PTT transcript: {transcript}")

        if not transcript.strip():
            return PTTResult(transcript="", response="", conversation_id=conversation_id)

        # 2. LLM response
        response, conv = await self.engine.chat(
            message=transcript,
            conversation_id=conversation_id,
            system_prompt=system_prompt,
            provider=llm_provider,
            model=llm_model,
        )

        # 3. Text-to-speech (optional)
        audio = None
        try:
            tts = self.voice_manager.get_tts(tts_provider)
            voice = tts_voice or "alloy"
            audio = await tts.synthesize(response, voice=voice)
        except Exception as e:
            logger.warning(f"TTS failed, returning text only: {e}")

        return PTTResult(
            transcript=transcript,
            response=response,
            audio=audio,
            conversation_id=conv.id,
        )
