from fastapi.testclient import TestClient

from modules.backend_integration_and_deployment.app import app

client = TestClient(app)


def test_health_endpoints_are_available_without_provider_credentials():
    assert client.get("/").status_code == 200
    assert client.get("/ping").json()["mode"] == "portfolio-demo"


def test_chat_rejects_empty_input_before_calling_a_provider():
    response = client.post("/chat", json={"user_id": "session-1", "text": "   "})
    assert response.status_code == 400


def test_chat_rejects_oversized_input_before_calling_a_provider(monkeypatch):
    monkeypatch.setenv("MAX_MESSAGE_CHARS", "3")
    response = client.post("/chat", json={"user_id": "session-1", "text": "hello"})
    assert response.status_code == 413


def test_transcription_rejects_non_audio_uploads():
    response = client.post(
        "/transcribe",
        files={"file": ("notes.txt", b"not audio", "text/plain")},
    )
    assert response.status_code == 415
