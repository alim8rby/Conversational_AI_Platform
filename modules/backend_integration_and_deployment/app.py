# modules/backend_integration_and_deployment/app.py

import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ───────────────────────────────────────────────────
# 1) Import the actual logic functions (not whole sub-apps)
#    We grab the *functions* from each module, rather than mounting their FastAPI objects.
# ───────────────────────────────────────────────────

# From your ASR server module (speech_to_text_asr/backend/server.py), import the logic:
from modules.speech_to_text_asr.backend.server import transcribe_endpoint as _transcribe_logic

# From your Chat backend module (llm_integration_and_prompting/chat_backend.py):
from modules.llm_integration_and_prompting.chat_backend import (
    ChatRequest, ChatResponse, chat_endpoint as _chat_logic
)

# ───────────────────────────────────────────────────
# 2) Create one “unified” FastAPI app that re-exposes those logic functions
# ───────────────────────────────────────────────────

app = FastAPI(title="El Consulto Unified API")

# CORS – allow both your local dev and your deployed front-end
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://el-consulto-frontend.onrender.com",       # your deployed React site
    "https://el-consulto-mvp-static.onrender.com",     # (if different)
    # Add any other production front-end URLs here
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ───────────────────────────────────────────────────
# 3) Re-expose the `/transcribe` endpoint exactly as it was
# ───────────────────────────────────────────────────

@app.post("/transcribe")
async def transcribe_endpoint(file: UploadFile = File(...)):
    """
    Proxy into your existing ASR logic (from server.py).
    """
    try:
        return await _transcribe_logic(file)
    except Exception as e:
        # If your original logic raised HTTPException, it will come through
        raise HTTPException(status_code=500, detail=f"ASR error: {e}")

# ───────────────────────────────────────────────────
# 4) Re-expose the `/chat` endpoint exactly as it was
# ───────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Proxy into your existing Chat logic (from chat_backend.py).
    """
    try:
        return await _chat_logic(req)
    except HTTPException as he:
        # If your chat logic already does raise HTTPException(…), allow it through
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {e}")

# ───────────────────────────────────────────────────
# 5) Add a health-check at `/ping` (and a root `/` if you want)
# ───────────────────────────────────────────────────

@app.get("/ping")
async def ping():
    return {"status": "El Consulto backend is alive"}

@app.get("/")
async def root():
    return {"status": "Welcome to El Consulto Backend"}

# (Any other endpoints can be added here as well)
