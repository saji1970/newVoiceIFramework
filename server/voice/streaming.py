from __future__ import annotations

import json
import logging

from fastapi import WebSocket

from server.core.engine import CoreEngine
from server.voice.manager import VoiceManager, VoiceSession

logger = logging.getLogger(__name__)


class VoiceStreamHandler:
    """Handles real-time voice streaming over WebSocket.

    Protocol:
    - Client sends: binary audio chunks OR JSON control messages
    - Server sends: JSON control messages AND binary audio chunks

    Control messages:
    - {"type": "config", "stt": "whisper", "tts": "openai", "voice": "alloy"}
    - {"type": "transcript", "text": "...", "final": true}
    - {"type": "response_start"}
    - {"type": "response_text", "text": "..."}
    - {"type": "response_end"}
    - {"type": "error", "message": "..."}
    """

    def __init__(self, engine: CoreEngine, voice_manager: VoiceManager):
        self.engine = engine
        self.voice_manager = voice_manager

    async def handle(self, websocket: WebSocket):
        session = self.voice_manager.create_session()
        await websocket.send_json({"type": "session_start", "session_id": session.id})

        audio_buffer: list[bytes] = []

        try:
            while session.active:
                message = await websocket.receive()

                if "text" in message:
                    await self._handle_control(websocket, session, json.loads(message["text"]))
                elif "bytes" in message:
                    audio_data = message["bytes"]
                    audio_buffer.append(audio_data)

                    # Process accumulated audio (simple VAD: process when no new audio for 500ms)
                    if len(audio_buffer) >= 10:  # ~1s of audio at typical chunk sizes
                        full_audio = b"".join(audio_buffer)
                        audio_buffer.clear()
                        await self._process_audio(websocket, session, full_audio)

        except Exception as e:
            logger.error(f"Voice stream error: {e}")
            try:
                await websocket.send_json({"type": "error", "message": str(e)})
            except Exception:
                pass
        finally:
            self.voice_manager.end_session(session.id)

    async def _handle_control(self, websocket: WebSocket, session: VoiceSession, msg: dict):
        msg_type = msg.get("type")

        if msg_type == "config":
            session.stt_provider = msg.get("stt", session.stt_provider)
            session.tts_provider = msg.get("tts", session.tts_provider)
            session.tts_voice = msg.get("voice", session.tts_voice)
            await websocket.send_json({"type": "config_ack"})

        elif msg_type == "end":
            session.active = False

    async def _process_audio(self, websocket: WebSocket, session: VoiceSession, audio: bytes):
        """STT → LLM → TTS pipeline."""
        try:
            # 1. Speech-to-text
            stt = self.voice_manager.get_stt(session.stt_provider)
            transcript = await stt.transcribe(audio)
            await websocket.send_json({"type": "transcript", "text": transcript, "final": True})

            if not transcript.strip():
                return

            # 2. LLM response
            await websocket.send_json({"type": "response_start"})
            response, conv = await self.engine.chat(
                message=transcript,
                conversation_id=session.conversation_id,
            )
            session.conversation_id = conv.id
            await websocket.send_json({"type": "response_text", "text": response})
            await websocket.send_json({"type": "response_end"})

            # 3. Text-to-speech
            tts = self.voice_manager.get_tts(session.tts_provider)
            async for audio_chunk in tts.stream_synthesize(response, voice=session.tts_voice):
                await websocket.send_bytes(audio_chunk)

            await websocket.send_json({"type": "audio_end"})

        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            await websocket.send_json({"type": "error", "message": str(e)})
