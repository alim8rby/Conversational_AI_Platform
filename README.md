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
     FastAPI
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

The application uses environment variables for external services and deployment-specific values. No API credentials should be committed to the repository.

## Evaluation

The project includes automated components for conversational quality and safety evaluation. The evaluation layer is designed to evolve toward reproducible regression testing, retrieval metrics, latency measurement, and multilingual quality checks.

## Engineering Focus

The project demonstrates separation of concerns across API integration, conversation orchestration, language processing, vector retrieval, speech processing, frontend interaction, and evaluation. It is intended as an engineering portfolio project and experimental conversational AI platform rather than a production service.

## Roadmap

- Centralize application configuration and dependency injection
- Add structured logging and observability
- Expand automated tests and mocked integration tests
- Add retrieval-quality and latency benchmarks
- Add CI for testing and linting
- Remove remaining legacy branding from internal paths

## License

No open-source license is currently specified.
