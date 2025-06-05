# modules/backend_integration_and_deployment/main_app.py

import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 1) ASR: speech-to-text
from modules.speech_to_text_asr.backend.app.services.asr import transcribe_audio

# 2) LLM chat: text-based chat
from modules.llm_integration_and_prompting.llm_service import LLMService

# Load API keys from environment (to be set later on Render or locally)
COHERE_API_KEY   = os.getenv("COHERE_API_KEY", "iqrvb7stR01Lv1fOhIawlBfUNGWSrIZI3W9WGDEp")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "pcsk_4sZacU_UpKYjb2sLr8p36QVFWRwNe5eg51xC8znXCx8iatJdznPzoUArhKt85y4wGUj6cY")
PINECONE_ENV     = os.getenv("PINECONE_ENV", "us-east-1")

if not COHERE_API_KEY or not PINECONE_API_KEY:
    raise RuntimeError("COHERE_API_KEY and PINECONE_API_KEY must be set as environment variables")

# Initialize the LLMService (handles Cohere + Pinecone internally)
llm_service = LLMService(cohere_api_key=COHERE_API_KEY)

# Initialize FastAPI app
app = FastAPI()

# Allow CORS so the React frontend can call these endpoints
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
    # Later, add your deployed frontend URL(s) here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ———————————————
# Endpoint 1: /transcribe  (ASR)
# ———————————————

@app.post("/transcribe")
async def transcribe_endpoint(file: UploadFile = File(...)):
    """
    Receives an audio file upload. Calls transcribe_audio(...) from Module 2.
    Returns JSON: { "text": "<transcript>" }.
    """
    audio_bytes = await file.read()
    try:
        transcript = transcribe_audio(audio_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ASR error: {e}")

    return {"text": transcript}


# ———————————————
# Endpoint 2: /chat       (LLM integration + memory)
# ———————————————

from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    text: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Receives JSON: { "user_id": "...", "text": "..." }.
    Calls llm_service.generate(...) and returns JSON: { "reply": "..." }.
    """
    user_id   = req.user_id.strip()
    user_text = req.text.strip()

    if not user_id or not user_text:
        raise HTTPException(status_code=400, detail="user_id and text are required")

    try:
        assistant_reply = llm_service.generate(user_id=user_id, user_message=user_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    return ChatResponse(reply=assistant_reply)


# ———————————————
# Health Check & Root
# ———————————————

@app.get("/")
async def root():
    return {"status": "El Consulto backend is running."}
