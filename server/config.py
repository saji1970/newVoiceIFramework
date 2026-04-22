from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    log_level: str = "info"

    # Auth
    api_key: str = "changeme"

    # Database
    database_url: str = "sqlite+aiosqlite:///./voicei.db"
    redis_url: str | None = None

    # LLM Providers
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    mistral_api_key: str | None = None
    cohere_api_key: str | None = None

    # Local providers
    ollama_base_url: str = "http://localhost:11434"
    vllm_base_url: str = "http://localhost:8080/v1"
    vllm_api_key: str | None = None

    # Voice
    deepgram_api_key: str | None = None
    elevenlabs_api_key: str | None = None

    # Defaults
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4o-mini"
    default_stt_provider: str = "whisper"
    default_tts_provider: str = "openai"
    default_tts_model: str = "tts-1"
    default_tts_voice: str = "alloy"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Pipeline config directory
    pipelines_dir: str = "pipelines"

    # Security: allowed modules for tool nodes in pipelines
    allowed_tool_modules: list[str] = []


settings = Settings()
