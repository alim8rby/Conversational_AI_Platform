import time

from cohere import ClientV2 as CohereClient

from modules.config import get_settings
from modules.language_detection_and_normalization.lang_detect import (
    detect_language,
    normalize_text,
    transliterate_franco,
)
from modules.memory_store_setup.memory_store import query_memory, upsert_memory


class LLMService:
    """Orchestrates multilingual dialogue, session-scoped memory, and LLM inference."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("COHERE_API_KEY is required to use the chat service")
        settings = get_settings()
        self.co = CohereClient(api_key)
        self.model = settings.llm_model
        self.top_k = settings.memory_top_k
        self.system_prompt = (
            "You are a concise, helpful conversational AI demo assistant. "
            "Use relevant retrieved context when it improves continuity. "
            "Do not invent facts that are not supported by the conversation or context. "
            "Respond in the user's language and keep responses natural and focused. "
            "You are not a medical professional: do not diagnose, prescribe, or provide "
            "emergency guidance. Encourage users in distress to contact a qualified "
            "professional or local emergency service."
        )

    def generate(self, user_id: str, user_message: str) -> str:
        lang = detect_language(user_message)

        if lang == "franco-arabic":
            user_text = normalize_text(transliterate_franco(user_message), "arabic")
            language_instruction = "Respond in Arabic."
        elif lang == "arabic":
            user_text = normalize_text(user_message, "arabic")
            language_instruction = "Respond in Arabic."
        else:
            user_text = normalize_text(user_message, "english")
            language_instruction = "Respond in English."

        try:
            matches = query_memory(user_id=user_id, query=user_text, top_k=self.top_k)
        except Exception:
            matches = []

        memory_lines = [
            f"- {match.get('metadata', {}).get('text_snippet')}"
            for match in matches
            if match.get("metadata", {}).get("text_snippet")
        ]

        context = self.system_prompt + "\n\n" + language_instruction
        if memory_lines:
            context += "\n\nRelevant conversation context:\n" + "\n".join(memory_lines)

        response = self.co.chat(
            model=self.model,
            temperature=0.4,
            max_tokens=200,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_text},
            ],
        )
        reply = response.message.content[0].text.strip()

        timestamp = int(time.time() * 1000)
        try:
            upsert_memory(
                id=f"{user_id}:user:{timestamp}",
                text=user_text,
                user_id=user_id,
                metadata={"role": "user", "text_snippet": user_text},
            )
            upsert_memory(
                id=f"{user_id}:assistant:{timestamp}",
                text=reply,
                user_id=user_id,
                metadata={"role": "assistant", "text_snippet": reply},
            )
        except Exception:
            # The demo remains useful when optional memory is unavailable.
            pass

        return reply
