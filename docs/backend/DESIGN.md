# Backend Architecture

Folders and files: [STRUCTURE.md](STRUCTURE.md). Data models and migrations: [SCHEMAS.md](SCHEMAS.md). Endpoints: [API.md](API.md). System architecture: [DESIGN.md](../DESIGN.md).

## Stack

- Python, FastAPI.
- Pydantic for data schema validation.
- SQLAlchemy and Alembic.
- PostgreSQL (Supabase).
- AI stack (LLM, LangChain, LangGraph, pgvector, evaluation): see [ai/DESIGN.md](../ai/DESIGN.md#stack).

## Modules

Contains services: modules responsible for a specific functionality according to DDD.

- `modules/auth` - authorization and registration logic. In v1.0 a simplified version: a browser session without registration. PostgreSQL. Details: [AUTH.md](AUTH.md).
- `modules/phones` - CRUD of phones, generation of the phone description and the model data (LLM) and antifraud logic (guardrails). PostgreSQL. AI part: see [ai/DESIGN.md](../ai/DESIGN.md#ai-in-the-backend-modules).
- `modules/rag` - contains the search logic and the search index. PostgreSQL with pgvector. AI part: see [ai/DESIGN.md](../ai/DESIGN.md#ai-in-the-backend-modules).
- `modules/main` - the service that provides a common API for the Frontend, and only it can call other services. It is also responsible for access checks and rate limit.

Each module can be moved to a separate microservice later, the `main` module can become a gateway: see [DESIGN.md](../DESIGN.md#backend).

## Indexing

The listing and its search index record are changed in one transaction: see [RAG.md](../ai/RAG.md#indexing).

Roadmap: see [ROADMAP.md](../ROADMAP.md#high-load).

## Protection

Cloudflare, rate limits and security rules: see [INFRA.md](../INFRA.md#protection).
