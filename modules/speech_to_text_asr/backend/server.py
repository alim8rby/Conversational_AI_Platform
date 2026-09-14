import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from modules.speech_to_text_asr.backend.app.services.asr import transcribe_audio

app = FastAPI(title="Speech-to-Text API")

origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"]
)


@app.post("/transcribe")
async def transcribe_endpoint(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Audio file is empty")

    try:
        transcript = transcribe_audio(audio_bytes)
        return {"text": transcript}
    except Exception as exc:
        print(f"ASR error: {exc}")
        raise HTTPException(status_code=500, detail="Transcription service unavailable") from exc


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
