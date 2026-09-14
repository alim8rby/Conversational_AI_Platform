import os
import time

from cohere import ClientV2 as CohereClient

from modules.language_detection_and_normalization.lang_detect import (
    detect_language,
    normalize_text,
    transliterate_franco,
)
from modules.memory_store_setup.memory_store import query_memory, upsert_memory


class LLMService:
    """Orchestrates multilingual dialogue, semantic memory, and LLM inference."""

    def __init__(self, api_key: str):
        self.co = CohereClient(api_key)
        self.model = os.getenv("LLM_MODEL", "command-r")
        self.top_k = int(os.getenv("MEMORY_TOP_K", "3"))
        self.system_prompt = (
            "You are a concise, helpful conversational AI assistant. "
            "Use relevant retrieved context when it improves continuity. "
            "Do not invent facts that are not supported by the conversation or context. "
            "Respond in the user's language and keep responses natural and focused."
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
            matches = query_memory(user_text, top_k=self.top_k)
        except Exception as exc:
            print(f"Memory retrieval warning: {exc}")
            matches = []

        memory_lines = []
        for match in matches:
            text = match.get("metadata", {}).get("text_snippet")
            if text:
                memory_lines.append(f"- {text}")

        context = self.system_prompt + "\n\n" + language_instruction
        if memory_lines:
            context += "\n\nRelevant conversation context:\n" + "\n".join(memory_lines)

        try:
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
        except Exception as exc:
            print(f"LLM error: {exc}")
            return "Sorry, the language service is temporarily unavailable."

        timestamp = int(time.time() * 1000)
        try:
            upsert_memory(
                id=f"{user_id}:user:{timestamp}",
                text=user_text,
                metadata={"user_id": user_id, "role": "user", "text_snippet": user_text},
            )
            upsert_memory(
                id=f"{user_id}:assistant:{timestamp}",
                text=reply,
                metadata={"user_id": user_id, "role": "assistant", "text_snippet": reply},
            )
        except Exception as exc:
            print(f"Memory persistence warning: {exc}")

        return reply
