# modules/backend_integration_and_deployment/app.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ───────────────────────────────────────────────
# 1) Import the two existing FastAPI apps
#    - ASR app serves /transcribe
#    - Chat app serves /chat
# ───────────────────────────────────────────────

# ASR FastAPI instance (in speech_to_text_asr/backend/server.py)
from modules.speech_to_text_asr.backend.server import app as asr_app

# Chat FastAPI instance (in llm_integration_and_prompting/chat_backend.py)
from modules.llm_integration_and_prompting.chat_backend import app as chat_app

# ───────────────────────────────────────────────
# 2) Create a “root” FastAPI instance and mount the two sub-apps
# ───────────────────────────────────────────────

app = FastAPI(title="El Consulto Unified API")

# CORS: allow both localhost (for dev) and the deployed React Static Site (for prod)
origins = [
    "http://localhost:5173",               # Vite dev server
    "http://127.0.0.1:5173",               # Vite dev server
    "https://el-consulto-mvp-static.onrender.com",  # your deployed React Static Site
    # If you host your frontend elsewhere (Netlify, etc.), add its URL here too.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Mount the ASR app at the root path:
#    /transcribe  → handled by asr_app (server.py)
app.mount("/", asr_app)

# Mount the Chat app under “/chat”:
#    /chat        → handled by chat_app (chat_backend.py)
app.mount("/chat", chat_app)

# Optional: a quick health-check at "/ping"
@app.get("/ping")
async def ping():
    return {"status": "El Consulto backend is alive"}
