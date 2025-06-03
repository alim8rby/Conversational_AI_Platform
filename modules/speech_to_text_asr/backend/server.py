# modules/speech-to-text-asr/backend/server.py

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# This import only works if you have __init__.py files as described above:
from app.services.asr import transcribe_audio

app = FastAPI()

# Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe")
async def transcribe_endpoint(file: UploadFile = File(...)):
    """
    Expects a multipart/form-data upload with a 'file' field.
    Returns JSON { "text": "the transcription" } or { "error": "<message>" }.
    """
    audio_bytes = await file.read()
    try:
        transcript = transcribe_audio(audio_bytes)
        return {"text": transcript}
    except Exception as e:
        # Print to the server console for debugging
        print("ASR error:", e)
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
