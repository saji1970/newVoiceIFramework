from __future__ import annotations

import base64

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.responses import Response
from pydantic import BaseModel

from server.dependencies import get_engine, verify_api_key
from server.core.engine import CoreEngine
from server.voice.manager import voice_manager
from server.voice.streaming import VoiceStreamHandler
from server.voice.push_to_talk import PushToTalkHandler

router = APIRouter(tags=["voice"])


class PTTResponse(BaseModel):
    transcript: str
    response: str
    audio_base64: str | None = None
    conversation_id: str | None = None


@router.websocket("/ws/voice/stream")
async def voice_stream_ws(websocket: WebSocket):
    """Real-time voice streaming via WebSocket.

    Protocol:
    - Client sends binary audio chunks or JSON control messages
    - Server responds with JSON control + binary audio chunks
    """
    await websocket.accept()
    try:
        engine = await get_engine()
        handler = VoiceStreamHandler(engine, voice_manager)
        await handler.handle(websocket)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass


@router.post("/voice/ptt", response_model=PTTResponse)
async def push_to_talk(
    audio: UploadFile = File(...),
    language: str = Form("en"),
    stt_provider: str | None = Form(None),
    tts_provider: str | None = Form(None),
    tts_voice: str | None = Form(None),
    llm_provider: str | None = Form(None),
    llm_model: str | None = Form(None),
    conversation_id: str | None = Form(None),
    system_prompt: str | None = Form(None),
    engine: CoreEngine = Depends(get_engine),
    _api_key: str = Depends(verify_api_key),
):
    """Push-to-talk: upload audio → get transcript + LLM response + audio back."""
    audio_data = await audio.read()
    audio_format = "wav"
    if audio.filename:
        ext = audio.filename.rsplit(".", 1)[-1].lower()
        if ext in ("wav", "mp3", "webm", "ogg", "flac", "m4a"):
            audio_format = ext

    handler = PushToTalkHandler(engine, voice_manager)
    result = await handler.process(
        audio_data=audio_data,
        audio_format=audio_format,
        language=language,
        stt_provider=stt_provider,
        tts_provider=tts_provider,
        tts_voice=tts_voice,
        llm_provider=llm_provider,
        llm_model=llm_model,
        conversation_id=conversation_id,
        system_prompt=system_prompt,
    )

    audio_b64 = None
    if result.audio:
        audio_b64 = base64.b64encode(result.audio).decode()

    return PTTResponse(
        transcript=result.transcript,
        response=result.response,
        audio_base64=audio_b64,
        conversation_id=result.conversation_id,
    )


@router.get("/voice/providers")
async def voice_providers(_api_key: str = Depends(verify_api_key)):
    """List available STT and TTS providers."""
    return {
        "stt": list(voice_manager._stt_providers.keys()),
        "tts": {
            name: provider.list_voices()
            for name, provider in voice_manager._tts_providers.items()
        },
    }
