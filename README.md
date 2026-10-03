# Conversational AI Platform

A portfolio project that demonstrates a full-stack, multilingual conversational-AI experience. It combines a React/Vite client, FastAPI API, Cohere-powered responses, session-scoped vector memory, speech-to-text, and lightweight evaluation utilities.

> **Portfolio demonstration only.** This repository is not a medical product, is not emergency support, and must not be used for clinical diagnosis, treatment, or high-stakes advice.

## Why this project

This project demonstrates practical AI-application engineering across a complete user flow:

- React/Vite chat interface with light/dark themes and microphone input
- FastAPI endpoints for chat and transcription
- English, Arabic, and Franco-Arabic normalization
- Cohere model integration with session-scoped Pinecone memory
- Whisper-based speech transcription
- Basic conversation-quality and safety-evaluation starting points
- GitHub Actions checks for backend tests and frontend lint/build

## Architecture

~~~text
React / Vite client
  ├─ browser-local session identifier
  ├─ text chat
  └─ audio capture
          │
          ▼
FastAPI API
  ├─ /chat → language normalization → Cohere → optional session memory
  └─ /transcribe → validated audio upload → Whisper
~~~

Memory is partitioned by the browser-local demo session. This keeps the demo’s conversations separate; it is not a replacement for a production authentication and privacy system.

## Quick start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Cohere API key for chat
- Pinecone API key for optional persistent memory

### Backend

~~~bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
uvicorn modules.backend_integration_and_deployment.app:app --reload
~~~

The API starts without provider credentials so health and input-validation endpoints can be tested. Set COHERE_API_KEY before sending chat requests. Pinecone is optional: if it is unavailable, chat continues without remembered context.

### Frontend

~~~bash
cd modules/frontend_chat_interface/el_consulto_frontend
npm ci
npm run dev
~~~

Set VITE_BACKEND_URL=http://localhost:8000 in the frontend environment when the frontend is served from a different origin.

## Configuration

Copy .env.example to .env.

| Variable | Purpose |
|---|---|
| COHERE_API_KEY | Enables the chat provider |
| PINECONE_API_KEY | Enables optional semantic memory |
| PINECONE_ENV | Pinecone serverless region |
| MEMORY_INDEX | Conversation-memory index name |
| LLM_MODEL | Cohere model name; defaults to command-r |
| MEMORY_TOP_K | Number of memories retrieved per message |
| MAX_MESSAGE_CHARS | Input length bound; defaults to 2,000 |
| MAX_UPLOAD_BYTES | Audio upload bound; defaults to 10 MiB |
| FRONTEND_ORIGINS | Comma-separated allowed local frontend origins |

Never commit a real .env file.

## Tests and quality checks

~~~bash
# Backend API and session-memory tests
pytest -q modules/evaluation_and_testing/tests

# Frontend
cd modules/frontend_chat_interface/el_consulto_frontend
npm run lint
npm run build
~~~

GitHub Actions runs these backend checks plus frontend lint/build on pull requests and the portfolio-polish branch.

## Repository map

~~~text
modules/
├── backend_integration_and_deployment/   # FastAPI application facade
├── evaluation_and_testing/               # API, memory, and evaluation checks
├── frontend_chat_interface/              # React/Vite client
├── language_detection_and_normalization/ # English/Arabic/Franco-Arabic helpers
├── llm_integration_and_prompting/        # Cohere orchestration
├── memory_store_setup/                   # Pinecone memory and knowledge helpers
└── speech_to_text_asr/                   # Whisper transcription
~~~

## Design decisions and limitations

This intentionally remains a compact portfolio project rather than a production platform. It does **not** implement user accounts, production-grade authorization, formal clinical safety review, data-retention controls, rate limiting, operational monitoring, or a full evaluation pipeline. Those are sensible future extensions, not claims this project makes today.

The knowledge scripts contain experimental mental-health-related examples solely to demonstrate retrieval plumbing. They are not medical content, professional guidance, or a substitute for qualified care.

## Next steps

- Add a version-pinned Python lockfile and dependency scan
- Expand multilingual regression and retrieval-quality evaluation
- Add screenshots or a short demo video to this README
- Containerize the local development workflow
- Add authenticated users only if the project scope grows beyond a portfolio demo

## License

No license has been selected yet. Add one before redistributing or accepting external contributions.
