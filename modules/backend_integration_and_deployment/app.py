from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from modules.config import get_settings
from modules.speech_to_text_asr.backend.server import transcribe_endpoint as _transcribe_logic
from modules.llm_integration_and_prompting.chat_backend import (
    ChatRequest,
    ChatResponse,
    chat_endpoint as _chat_logic,
)

settings = get_settings()
app = FastAPI(title="Conversational AI Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.post("/transcribe")
async def transcribe_endpoint(file: UploadFile = File(...)):
    """Proxy to the speech-to-text service."""
    try:
        return await _transcribe_logic(file)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Speech-to-text service unavailable") from exc


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """Proxy to the conversational AI service."""
    return await _chat_logic(req)


@app.get("/ping")
async def ping():
    return {"status": "ok", "mode": "portfolio-demo"}


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Conversational AI Platform API",
        "notice": "Portfolio demonstration; not medical advice.",
    }
