# modules/llm_integration_and_prompting/chat_backend.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import your existing LLMService exactly as it is
from modules.llm_integration_and_prompting.llm_service import LLMService

app = FastAPI()

#
# === CORS CONFIGURATION ===
# Allow your React frontend (running on port 5173) to call this API.
#
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Frontend origin(s)
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

#
# === PLACEHOLDER FOR YOUR COHERE API KEY ===
# Edit the line below and replace <YOUR_COHERE_API_KEY> with your actual key.
#
COHERE_API_KEY = "iqrvb7stR01Lv1fOhIawlBfUNGWSrIZI3W9WGDEp"

# Instantiate the service using the key above.
# If you ever want to pull it from an environment variable or other config,
# just update this line accordingly.
llm_service = LLMService(COHERE_API_KEY)


#
# === REQUEST/RESPONSE MODELS ===
#
class ChatRequest(BaseModel):
    user_id: str
    text: str

class ChatResponse(BaseModel):
    reply: str


#
# === CHAT ENDPOINT ===
# Expects JSON: { "user_id": "some_unique_id", "text": "Hello, how are you?" }
#
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    user_id   = req.user_id.strip()
    user_text = req.text.strip()

    if not user_id or not user_text:
        raise HTTPException(status_code=400, detail="user_id and text are required")

    # Delegate to your existing LLMService.generate(...)
    assistant_reply = llm_service.generate(user_id=user_id, user_message=user_text)
    return ChatResponse(reply=assistant_reply)
