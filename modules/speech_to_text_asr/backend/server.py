from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from modules.config import get_settings
from modules.speech_to_text_asr.backend.app.services.asr import transcribe_audio

settings = get_settings()
app = FastAPI(title="Speech-to-Text API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.post("/transcribe")
async def transcribe_endpoint(file: UploadFile = File(...)):
    if not (file.content_type or "").startswith("audio/"):
        raise HTTPException(status_code=415, detail="Upload must be an audio file")

    audio_bytes = await file.read(settings.max_upload_bytes + 1)
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Audio file is empty")
    if len(audio_bytes) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Audio files are limited to {settings.max_upload_bytes} bytes",
        )

    try:
        transcript = transcribe_audio(audio_bytes, filename=file.filename or "")
        return {"text": transcript}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Transcription service unavailable") from exc


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
