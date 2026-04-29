# RAG Knowledgebase Backend

Production-grade multi-tenant RAG backend for internal company knowledge assistants.

## Overview

This service lets organizations upload internal files, ingest them into pgvector, and ask grounded questions using OpenRouter LLMs.

Key capabilities:
- JWT auth and org-scoped access
- Document upload and parsing (`PDF`, `DOCX`, `TXT`, `MD`)
- Chunking + overlap strategy for retrieval quality
- Vector embeddings stored in PostgreSQL `pgvector`
- Semantic search and RAG answering with source citations
- Chat history, admin APIs, and dashboard analytics

## RAG Architecture

```text
Client -> FastAPI -> UploadService -> Parser -> ChunkService
                                     -> EmbeddingService -> PostgreSQL(pgvector)
Client -> /chat/ask -> EmbeddingService(question) -> Vector Similarity Search
                   -> LLMService(OpenRouter with context) -> grounded answer + sources
```

## Tech Stack

- Python 3.11+, FastAPI, SQLAlchemy, Alembic
- PostgreSQL + pgvector
- Pydantic v2
- OpenRouter API
- Docker + Docker Compose
- Pytest

## Project Structure

```text
app/
  api/routes/
  core/
  db/
  models/
  schemas/
  services/
  workers/
  utils/
  tests/
main.py
```

## Setup

1. Copy envs:
   - `cp .env.example .env`
2. Start services:
   - `docker compose up --build`
3. Run migrations:
   - `alembic upgrade head`
4. Open docs:
   - `http://localhost:8000/docs`
   - `http://localhost:8000/redoc`

## Environment Variables

- `DATABASE_URL`
- `JWT_SECRET`
- `OPENROUTER_API_KEY`
- `OPENROUTER_BASE_URL`
- `UPLOAD_DIR`
- `PORT`

## pgvector Notes

- Migration enables extension:
  - `CREATE EXTENSION IF NOT EXISTS vector;`
- Embeddings stored in `document_chunks.embedding`
- Similarity retrieval uses cosine distance in SQL

## OpenRouter Notes

- Set `OPENROUTER_API_KEY` in `.env`
- Default base URL:
  - `https://openrouter.ai/api/v1`
- You can use free-tier models (Qwen/Mistral/DeepSeek/Llama variants)

## Sample Workflow

1. Create organization
2. Register and login user
3. Upload document
4. Wait for indexing status = `indexed`
5. Ask question via `/api/v1/chat/ask`
6. Inspect answer confidence + source chunks

## Assumptions

- Background processing uses FastAPI `BackgroundTasks` by default.
- Embeddings default to OpenRouter; local deterministic fallback is used if API key is absent.
- Access control defaults to org-wide visibility unless explicitly restricted.
