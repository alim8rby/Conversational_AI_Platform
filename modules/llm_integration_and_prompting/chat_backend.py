import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from modules.llm_integration_and_prompting.llm_service import LLMService

app = FastAPI(title="Conversational AI API")

API_KEY = os.getenv("COHERE_API_KEY")
if not API_KEY:
    raise RuntimeError("LLM configuration is missing")

llm_service = LLMService(API_KEY)


class ChatRequest(BaseModel):
    user_id: str
    text: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    user_id = req.user_id.strip()
    user_text = req.text.strip()

    if not user_id or not user_text:
        raise HTTPException(status_code=400, detail="user_id and text are required")

    try:
        reply = llm_service.generate(user_id=user_id, user_message=user_text)
        return ChatResponse(reply=reply)
    except Exception as exc:
        print(f"LLM service error: {exc}")
        raise HTTPException(status_code=500, detail="LLM service unavailable") from exc
