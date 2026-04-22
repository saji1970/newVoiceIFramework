from __future__ import annotations

import json
from typing import AsyncIterator


async def sse_stream(event_stream: AsyncIterator[str], event_type: str = "chunk"):
    """Wrap an async string iterator as Server-Sent Events."""
    async for chunk in event_stream:
        data = json.dumps({"type": event_type, "content": chunk})
        yield f"data: {data}\n\n"
    yield f"data: {json.dumps({'type': 'done'})}\n\n"
