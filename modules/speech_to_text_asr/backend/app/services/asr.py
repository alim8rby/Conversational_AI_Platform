# modules/speech-to-text-asr/backend/app/services/asr.py

import os
import tempfile
from transformers import pipeline

_asr_pipeline = None

def load_asr_model():
    global _asr_pipeline
    if _asr_pipeline is None:
        _asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-base",
            chunk_length_s=30
        )
    return _asr_pipeline

def transcribe(audio_path: str):
    """
    Transcribe an audio file from disk and return the text (no language).
    """
    asr = load_asr_model()
    result = asr(audio_path)
    text = result.get("text", "").strip()
    return text

def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Write the raw bytes to a temp file, call `transcribe(path)`, then delete it.
    Returns the transcription string. Raises any exceptions from the pipeline.
    """
    # Create a temp file with .wav suffix
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        temp_path = tmp.name
        tmp.write(audio_bytes)

    try:
        transcript = transcribe(temp_path)
        return transcript
    finally:
        # Clean up the temp file
        try:
            os.remove(temp_path)
        except OSError:
            pass
