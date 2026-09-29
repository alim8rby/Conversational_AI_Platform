# Architecture

## Target architecture
Clients → API Gateway → Conversation Services → Model/Prompt/Memory Providers → Persistence → Evaluation/Observability.

## Platform principle
Separate reusable platform interfaces from provider-specific implementations so models, prompts, memory backends, and consumers can evolve independently.
