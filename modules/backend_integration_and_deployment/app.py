import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from modules.speech_to_text_asr.backend.server import transcribe_endpoint as _transcribe_logic
from modules.llm_integration_and_prompting.chat_backend import (
    ChatRequest,
    ChatResponse,
    chat_endpoint as _chat_logic,
)

app = FastAPI(title="Conversational AI Platform API")

origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.post("/transcribe")
async def transcribe_endpoint(file: UploadFile = File(...)):
    """Proxy to the speech-to-text service."""
    try:
        return await _transcribe_logic(file)
    except HTTPException:
        raise
    except Exception as exc:
        print(f"ASR service error: {exc}")
        raise HTTPException(status_code=500, detail="Speech-to-text service unavailable") from exc


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """Proxy to the conversational AI service."""
    try:
        return await _chat_logic(req)
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Chat service error: {exc}")
        raise HTTPException(status_code=500, detail="Conversational AI service unavailable") from exc


@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"status": "ok", "service": "Conversational AI Platform API"}
