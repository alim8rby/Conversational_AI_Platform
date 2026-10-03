import os
import tempfile
from pathlib import Path

from transformers import pipeline

_asr_pipeline = None


def load_asr_model():
    global _asr_pipeline
    if _asr_pipeline is None:
        _asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-base",
            chunk_length_s=30,
        )
    return _asr_pipeline


def transcribe(audio_path: str) -> str:
    result = load_asr_model()(audio_path)
    return result.get("text", "").strip()


def transcribe_audio(audio_bytes: bytes, filename: str = "") -> str:
    """Transcribe uploaded audio and always remove its temporary file."""
    suffix = Path(filename).suffix.lower()
    if suffix not in {".wav", ".webm", ".mp3", ".m4a", ".ogg"}:
        suffix = ".webm"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        temp_path = tmp.name
        tmp.write(audio_bytes)

    try:
        return transcribe(temp_path)
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass
