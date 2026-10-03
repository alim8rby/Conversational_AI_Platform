"""Centralized, lightweight configuration for the portfolio demo."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    cohere_api_key: str | None
    pinecone_api_key: str | None
    pinecone_region: str
    memory_index: str
    frontend_origins: list[str]
    llm_model: str
    memory_top_k: int
    max_message_chars: int
    max_upload_bytes: int


def _int_env(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return max(1, value)


def get_settings() -> Settings:
    origins = [
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ]
    return Settings(
        cohere_api_key=os.getenv("COHERE_API_KEY"),
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
        pinecone_region=os.getenv("PINECONE_ENV", "us-east-1"),
        memory_index=os.getenv("MEMORY_INDEX", "conversation-memory"),
        frontend_origins=origins,
        llm_model=os.getenv("LLM_MODEL", "command-r"),
        memory_top_k=_int_env("MEMORY_TOP_K", 3),
        max_message_chars=_int_env("MAX_MESSAGE_CHARS", 2_000),
        max_upload_bytes=_int_env("MAX_UPLOAD_BYTES", 10 * 1024 * 1024),
    )
