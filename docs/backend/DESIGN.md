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

## Configuration

- Each module reads its settings from environment variables and `backend/.env` (template: `backend/.env.example`). The path to `backend/.env` is resolved from the settings file (`core/config.py`, `modules/main/config.py`), so the settings do not depend on the current directory. Environment variables take precedence over `backend/.env`. Secrets: see [INFRA.md](../INFRA.md).
- `core`: `DATABASE_URL` (required).
- `modules/main`: `CORS_ORIGINS` (optional, default `http://localhost:3000`).
- On startup `modules/main` collects the configuration errors of `core` and of the modules and stops the process with the list of missing or invalid variables. The API does not start with an incomplete configuration.
- `make backend-check` runs the same check before `make backend-dev`, `make migrate` and `make up-all`, so the command stops with a non-zero exit code instead of leaving the reloader running.

## Database connection

- All modules use one PostgreSQL database and one connection: `core/database.py` creates one SQLAlchemy engine with one connection pool from `DATABASE_URL`.
- One session and one transaction per request, shared by all modules while the Backend is a monolith. Why: see [Tradeoffs](#shared-session-in-the-monolith).
  - `modules/main` opens the session of the request with the `DbSession` dependency and passes it to every service call of the request.
  - The transaction is committed when the endpoint returns, before the response is sent. An error in the request rolls it back, so the changes of all modules in the request are saved together or not at all.
  - Service functions take the session as the first argument and never commit or open their own session. They return Pydantic schemas, never ORM objects.
  - Slow external calls (LLM, embeddings) run before the database work of the request, so the request does not hold a connection while it waits.
- Each module keeps its tables on its own declarative Base (`AuthBase`): no foreign keys between modules, see [SCHEMAS.md](SCHEMAS.md#migrations).
- `core` contains infrastructure only, no domain logic.

## Indexing

The listing and its search index record are changed in one transaction: see [RAG.md](../ai/RAG.md#indexing).

Roadmap: see [ROADMAP.md](../ROADMAP.md#high-load).

## Protection

Cloudflare, rate limits and security rules: see [INFRA.md](../INFRA.md#protection).

## Tradeoffs

### Shared session in the monolith

- One transaction across modules without a distributed transaction or an outbox: the listing and its search index record are saved together ([RAG.md](../ai/RAG.md#indexing)).
- Limitation: works only while the modules share one database. A module moved to a separate service loses the shared transaction, its calls go through a client, and cross-module consistency needs an outbox or a saga.
- Rejected: a session per service call. Simpler module isolation, but a request that changes two modules can leave one change saved and the other lost.
