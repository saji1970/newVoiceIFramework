from __future__ import annotations

import json
from typing import AsyncIterator

import httpx

from server.config import settings
from server.providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self):
        self.base_url = settings.ollama_base_url.rstrip("/")

    def is_available(self) -> bool:
        # Ollama is available if the URL is set (local-only, no API key needed)
        return bool(self.base_url)

    def list_models(self) -> list[str]:
        return ["llama3.1", "llama3", "mistral", "codellama", "phi3", "gemma2"]

    async def chat(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]

    async def stream(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> AsyncIterator[str]:
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content

    async def embeddings(
        self, texts: list[str], model: str = "nomic-embed-text", **kwargs
    ) -> list[list[float]]:
        results = []
        async with httpx.AsyncClient(timeout=60) as client:
            for text in texts:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": model, "prompt": text},
                )
                response.raise_for_status()
                results.append(response.json()["embedding"])
        return results
