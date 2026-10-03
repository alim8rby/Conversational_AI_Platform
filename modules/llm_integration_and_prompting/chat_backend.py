from functools import lru_cache

from fastapi import HTTPException
from pydantic import BaseModel

from modules.config import get_settings
from modules.llm_integration_and_prompting.llm_service import LLMService


class ChatRequest(BaseModel):
    user_id: str
    text: str


class ChatResponse(BaseModel):
    reply: str


@lru_cache(maxsize=1)
def get_llm_service() -> LLMService:
    settings = get_settings()
    if not settings.cohere_api_key:
        raise RuntimeError("COHERE_API_KEY is not configured")
    return LLMService(settings.cohere_api_key)


async def chat_endpoint(req: ChatRequest) -> ChatResponse:
    user_id = req.user_id.strip()
    user_text = req.text.strip()
    settings = get_settings()

    if not user_id or not user_text:
        raise HTTPException(status_code=400, detail="user_id and text are required")
    if len(user_text) > settings.max_message_chars:
        raise HTTPException(
            status_code=413,
            detail=f"Messages are limited to {settings.max_message_chars} characters",
        )

    try:
        reply = get_llm_service().generate(user_id=user_id, user_message=user_text)
        return ChatResponse(reply=reply)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Language provider is unavailable") from exc
