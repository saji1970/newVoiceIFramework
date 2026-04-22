from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from server.core.engine import CoreEngine
from server.dependencies import get_engine, verify_api_key

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    system_prompt: str | None = None
    provider: str | None = None
    model: str | None = None
    temperature: float = Field(0.7, ge=0, le=2)
    max_tokens: int = Field(2048, ge=1, le=128000)
    stream: bool = False


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    provider: str | None = None
    model: str | None = None


@router.post("/chat")
async def chat(
    request: ChatRequest,
    engine: CoreEngine = Depends(get_engine),
    _api_key: str = Depends(verify_api_key),
):
    if request.stream:
        return await chat_stream(request, engine)

    response, conv = await engine.chat(
        message=request.message,
        conversation_id=request.conversation_id,
        system_prompt=request.system_prompt,
        provider=request.provider,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )
    return ChatResponse(
        response=response,
        conversation_id=conv.id,
        provider=request.provider,
        model=request.model,
    )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    engine: CoreEngine = Depends(get_engine),
    _api_key: str = Depends(verify_api_key),
):
    stream, conv = await engine.chat_stream(
        message=request.message,
        conversation_id=request.conversation_id,
        system_prompt=request.system_prompt,
        provider=request.provider,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )

    async def event_generator():
        import json

        yield json.dumps({"type": "start", "conversation_id": conv.id})
        async for chunk in stream:
            yield json.dumps({"type": "chunk", "content": chunk})
        yield json.dumps({"type": "done"})

    return EventSourceResponse(event_generator())


@router.get("/conversations")
async def list_conversations(
    engine: CoreEngine = Depends(get_engine),
    _api_key: str = Depends(verify_api_key),
):
    return {"conversations": engine.conversations.list_ids()}


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    engine: CoreEngine = Depends(get_engine),
    _api_key: str = Depends(verify_api_key),
):
    conv = engine.conversations.get(conversation_id)
    if conv is None:
        from fastapi import HTTPException

        raise HTTPException(404, "Conversation not found")
    return {
        "id": conv.id,
        "messages": [
            {"role": m.role, "content": m.content, "timestamp": m.timestamp} for m in conv.messages
        ],
        "created_at": conv.created_at,
    }
