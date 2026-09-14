# Conversational AI Platform

A full-stack conversational AI platform combining LLM-powered dialogue, multilingual processing, semantic memory, speech-to-text, and automated evaluation.

## Highlights

- **LLM dialogue** — Cohere-powered conversational generation with configurable prompts.
- **Semantic memory** — Pinecone vector retrieval for context-aware conversations.
- **Multilingual interaction** — English, Arabic, and Franco-Arabic detection and normalization.
- **Voice input** — Audio transcription through an ASR pipeline.
- **Evaluation** — Coherence, empathy, and safety evaluation components.
- **Web interface** — React/Vite client connected to a FastAPI backend.

## Architecture

```text
React / Vite Client
        │
        ▼
     FastAPI API
        │
        ▼
Conversation Service
   ┌────┼──────────────┐
   ▼    ▼              ▼
  LLM  Memory          ASR
   │    │              │
Cohere Pinecone     Speech Model
        │
        ▼
   Evaluation
```

## Repository Structure

```text
modules/
├── backend_integration_and_deployment/
├── evaluation_and_testing/
├── frontend_chat_interface/
├── language_detection_and_normalization/
├── llm_integration_and_prompting/
├── memory_store_setup/
└── speech_to_text_asr/
```

## Running Locally

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file from `.env.example` and provide the required service credentials.

```bash
uvicorn modules.backend_integration_and_deployment.app:app --reload
```

### Frontend

```bash
cd modules/frontend_chat_interface/el_consulto_frontend
npm install
npm run dev
```

## Configuration

Deployment-specific values and external service credentials are supplied through environment variables. API credentials are intentionally excluded from version control.

See `.env.example` for the available configuration variables.

## Evaluation

The repository includes components for conversational quality and safety evaluation. The evaluation layer is intended to support reproducible regression testing, retrieval-quality metrics, latency benchmarks, and multilingual quality checks.

## Engineering Focus

The project demonstrates separation of concerns across API integration, conversation orchestration, language processing, vector retrieval, speech processing, frontend interaction, evaluation, and CI.

It is an engineering portfolio project and experimental conversational AI platform rather than a production service.

## Next Improvements

- Centralize application configuration and dependency injection
- Add structured logging and observability
- Expand automated unit and integration tests
- Add retrieval-quality and latency benchmarks
- Remove remaining legacy branding from internal paths

## License

No open-source license is currently specified.
