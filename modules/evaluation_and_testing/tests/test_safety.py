"""Offline checks for the portfolio demo's safety instruction boundary."""

from modules.llm_integration_and_prompting.llm_service import LLMService


class FakeCohere:
    def __init__(self):
        self.messages = None

    def chat(self, **kwargs):
        self.messages = kwargs["messages"]
        message = type("Message", (), {"content": [type("Part", (), {"text": "Please contact a qualified professional."})()]})()
        return type("Response", (), {"message": message})()


def test_health_boundary_is_included_in_the_provider_instruction(monkeypatch):
    monkeypatch.setattr(
        "modules.llm_integration_and_prompting.llm_service.query_memory",
        lambda **kwargs: [],
    )
    monkeypatch.setattr(
        "modules.llm_integration_and_prompting.llm_service.upsert_memory",
        lambda **kwargs: None,
    )

    service = LLMService("test-key")
    fake_cohere = FakeCohere()
    service.co = fake_cohere

    reply = service.generate("session-1", "Should I stop my antidepressant?")

    system_instruction = fake_cohere.messages[0]["content"].lower()
    assert "not a medical professional" in system_instruction
    assert "do not diagnose" in system_instruction
    assert "emergency service" in system_instruction
    assert "qualified professional" in reply.lower()
