# example_usage.py

from llm_service import LLMService

if __name__ == "__main__":
    # 1) Hardcode your Cohere trial key here (no extra spaces or line breaks):
    api_key = "iqrvb7stR01Lv1fOhIawlBfUNGWSrIZI3W9WGDEp"
    # Replace "YOUR_COHERE_TRIAL_API_KEY" with your exact key from the Cohere dashboard.

    # 2) Instantiate LLMService for v2 Chat
    llm = LLMService(
        api_key=api_key,
        model_name="command-xlarge-nightly",   # Chat-enabled on trial
        max_tokens=512,
        temperature=0.7
    )

    # 3) Memory/context about your startup
    memory = (
        "El Consulto is a medical startup building an AI “therapist” that simulates a "
        "one-hour session. It should collect a complete psychiatric sheet (ICD-11–compatible) "
        "and offer psychological assessments, then guide the user through a healing journey "
        "without requiring pharmacological intervention unless clinically indicated."
    )

    # 4) Example conversation history up to this point
    history = [
        ("user", "Hello, I’d like help with my anxiety."),
        ("assistant", "Of course. To begin, can you tell me how long you’ve been feeling anxious?")
    ]

    # 5) Latest user message
    user_msg = "I’ve felt anxious for about six months, mostly at work."

    # 6) Generate the assistant’s reply via Cohere v2 Chat
    reply = llm.generate(memory, history, user_msg)

    print("\n🤖 Assistant says:", reply)
