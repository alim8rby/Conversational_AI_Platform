# modules/llm_integration_and_prompting/llm_service.py

import time
from cohere import ClientV2 as CohereClient    # <— Use ClientV2, not Client

# Pinecone helpers
from modules.memory_store_setup.memory_store import upsert_memory, query_memory

# Language detection & normalization from Module 3
from modules.speech_to_text_asr.backend.app.services.lang_detect import (
    detect_language,
    normalize_text,
    transliterate_franco
)

class LLMService:
    def __init__(self, cohere_api_key: str):
        """
        Initialize the Cohere v2 client and set your static prompt context.
        Make sure you pass a valid Cohere API key here.
        """
        # Instantiate the v2 client
        self.co = CohereClient(cohere_api_key)

        # A rich static context for “therapist style”
        self.static_context = """
You are an experienced, empathetic psychiatrist conducting a therapy session.
Your goal is to build rapport, gather important clinical information organically,
and gently guide the client toward insight and coping strategies.
You will:

1. **Start each session** with a warm, concise check‐in—“How have you been feeling since our last conversation?”—to encourage the client to share whatever is most pressing.
2. **Ask only one question at a time**, reflecting back what the client says (“I hear you saying…”), so they feel heard and not rushed.
3. **Gather diagnostic clues** naturally by exploring:
   • Mood (e.g., “Over the past week, have you noticed changes in your sleep or appetite?”)
   • Energy and motivation
   • Thoughts and beliefs (e.g., “What goes through your mind when you feel that way?”)
   • Behaviors (e.g., “How are you coping on a day-to-day basis?”)
   • Interpersonal and occupational impacts
   As you do, you may implicitly reference ICD-11 definitions (e.g., “When I say ‘persistent worry,’ I mean the kind of constant worry that lasts most days for at least two weeks.”), but you do **not** read off a checklist.
4. **Draw on relevant therapy approaches**—for instance:
   • Cognitive‐Behavioral techniques (explore thoughts ↔ feelings ↔ behaviors)
   • Acceptance & Commitment Therapy (validate feelings, explore values)
   • Psychodynamic “why does this matter to you now?” questions if the client describes patterns
   • Gentle motivational interviewing (“What would you like to see change?”)
   But you blend these approaches seamlessly based on the client’s responses and emotional state.
5. **Validate emotions** (“That sounds very difficult… I can see why you’d feel that way”) before moving on to the next question.
6. When enough information suggests a diagnostic possibility, you can gently say, “Sometimes, these symptoms align with what the ICD-11 calls [brief name], but remember this is just an initial thought—you’d want to explore further with a full assessment.”
7. **Offer coping strategies and psychoeducation** (e.g., a simple breathing exercise, a cognitive reframing technique, or a helpful resource) when appropriate, rather than jumping into them too early.
8. Keep your language **concise** and **professional**, yet warm—no jargon unless you explain it in plain English (or Arabic, depending on the user’s language).
9. **End each turn** with a question or invitation that feels natural: “Is that making sense so far?” or “Would you like to tell me more about how that affects your daily life?”

Whenever you send a response, use the most recent user message, any retrieved memory snippets, and this context as your guide. Your overall style should be that of a skilled clinician who:
- Listens actively
- Gathers clinical data without making it feel like a form
- Uses ICD-11 language sparingly and gently
- Flexibly draws on CBT, ACT, psychodynamic, or other modalities as needed
- Invites the client to reflect on meaning, coping, and values, not just symptom checklists.

Begin now.
""".strip()

    def generate(self, user_id: str, user_message: str) -> str:
        """
        1) Detect user language (arabic, english, or franco-arabic)
        2) Normalize Franco-Arabic into Arabic text if needed
        3) Retrieve top-k memories
        4) Build system prompt (with language instruction)
        5) Call Cohere chat(...)  # <— v2 style
        6) Upsert memory
        7) Return reply
        """

        # ——————————————————————————————
        # 1) DETECT & NORMALIZE USER INPUT
        # ——————————————————————————————
        lang = detect_language(user_message)

        if lang == "franco-arabic":
            normalized_input = transliterate_franco(user_message)
            normalized_input = normalize_text(normalized_input, "arabic")
            user_text_for_model = normalized_input
            language_instruction = "Please respond in Arabic."
        elif lang == "arabic":
            normalized_input = normalize_text(user_message, "arabic")
            user_text_for_model = normalized_input
            language_instruction = "Please respond in Arabic."
        else:
            user_text_for_model = normalize_text(user_message, "english")
            language_instruction = "Please respond in English."

        # ——————————————————————————————
        # 2) RETRIEVE PAST MEMORIES
        # ——————————————————————————————
        top_k = 3
        try:
            matches = query_memory(user_text_for_model, top_k=top_k)
        except Exception as e:
            print("⚠️ Warning: Pinecone query failed:", e)
            matches = []

        memory_block = ""
        for m in matches:
            snippet = m.get("metadata", {}).get("text_snippet")
            if snippet:
                memory_block += f"- {snippet}\n"

        # ——————————————————————————————
        # 3) BUILD THE FULL SYSTEM PROMPT
        # ——————————————————————————————
        parts = [
            self.static_context,
            language_instruction
        ]

        if memory_block:
            parts.append("Relevant Past Session Snippets:\n" + memory_block)

        system_prompt = "\n\n".join(parts)

        # ——————————————————————————————
        # 4) CALL COHERE CHAT COMPLETION (v2)
        # ——————————————————————————————
        try:
            response = self.co.chat(
                model="command-xlarge-nightly",   # chat-only model
                temperature=0.7,
                max_tokens=150,
                messages=[
                    {"role": "system",  "content": system_prompt},
                    {"role": "user",    "content": user_text_for_model}
                ],
            )
            # Extract the assistant’s reply text from v2 response
            assistant_reply = response.message.content[0].text.strip()
        except Exception as e:
            print("❌ Error calling Cohere chat API:", e)
            if lang in ("arabic", "franco-arabic"):
                return "⚠️ آسف، أواجه صعوبة في التفكير الآن. حاول مرة أخرى."
            else:
                return "⚠️ Sorry, I’m having trouble thinking right now. Please try again."

        # ——————————————————————————————
        # 5) UPSERT USER & ASSISTANT INTO PINECONE
        # ——————————————————————————————
        ts = int(time.time() * 1000)
        try:
            upsert_memory(
                id=f"{user_id}:user:{ts}",
                text=user_text_for_model,
                metadata={"role": "user", "text_snippet": user_text_for_model},
            )
        except Exception as e:
            print("⚠️ Warning: Pinecone upsert (user) failed:", e)

        try:
            upsert_memory(
                id=f"{user_id}:assistant:{ts}",
                text=assistant_reply,
                metadata={"role": "assistant", "text_snippet": assistant_reply},
            )
        except Exception as e:
            print("⚠️ Warning: Pinecone upsert (assistant) failed:", e)

        # ——————————————————————————————
        # 6) RETURN THE ASSISTANT’S REPLY
        # ——————————————————————————————
        return assistant_reply
