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

- `modules/users` - CRUD of users. PostgreSQL. Details: [AUTH.md](AUTH.md#modules).
- `modules/auth` - authorization: the session token, the authentication of a request and the owner check. In v1.0 a simplified version: a browser session without registration, no tables. Details: [AUTH.md](AUTH.md).
- `modules/phones` - CRUD of phones, generation of the phone description and the model data (LLM) and antifraud logic (guardrails). PostgreSQL. AI part: see [ai/DESIGN.md](../ai/DESIGN.md#ai-in-the-backend-modules).
- `modules/rag` - contains the search logic and the search index. PostgreSQL with pgvector. AI part: see [ai/DESIGN.md](../ai/DESIGN.md#ai-in-the-backend-modules).
- `modules/main` - the service that provides a common API for the Frontend. It is also responsible for the session cookie, access checks and rate limit.

Module calls:

- `modules/main` calls the public interface of every domain module: `services/`, see [STRUCTURE.md](STRUCTURE.md#domain-module).
- `modules/auth` calls `users.services`: the user of a session token must exist.
- No other calls between domain modules.

Each module can be moved to a separate microservice later, the `main` module can become a gateway: see [DESIGN.md](../DESIGN.md#backend).

## Configuration

- Each module reads its settings from environment variables and `backend/.env` (template: `backend/.env.example`). The path to `backend/.env` is resolved from the settings file (`core/config.py` and the `config.py` of each module), so the settings do not depend on the current directory. Environment variables take precedence over `backend/.env`. Secrets: see [INFRA.md](../INFRA.md).
- `core`: `DATABASE_URL` (required).
- `modules/main`: `CORS_ORIGINS` (optional, default `http://localhost:3000`), `SESSION_SECRET` (required, at least 32 characters, passed to `modules/auth`), `COOKIE_SECURE` (optional, default `true`). Session and cookie: see [AUTH.md](AUTH.md#session-token).
- `modules/phones`: `OPENAI_API_KEY` (required), `DESCRIPTION_MODEL` (optional, default `gpt-5.6-luna`), `GUARDRAIL_MODEL` (optional, default `gpt-5.6-luna`, see [GUARDRAILS.md](../ai/GUARDRAILS.md#model)).
- `modules/rag`: `OPENAI_API_KEY` (required), `EMBEDDING_MODEL` (optional, default `text-embedding-3-small`, see [SCHEMAS.md](SCHEMAS.md#search_index-modulesrag)).
- `modules/phones` and `modules/rag` create their LangChain clients from their own settings with the factories of `core/llm.py` (`max_retries=2`, see [RAG.md](../ai/RAG.md#errors-and-retries)). `modules/main` passes no AI clients to the service calls.
- On startup `modules/main` collects the configuration errors of `core` and of the modules (a variable shared by several modules is listed once) and stops the process with the list of missing or invalid variables. The API does not start with an incomplete configuration.
- `make backend-check` runs the same check before `make backend-dev`, `make migrate` and `make up-all`, so the command stops with a non-zero exit code instead of leaving the reloader running.

## Database connection

- All modules use one PostgreSQL database and one connection: `core/database.py` creates one SQLAlchemy engine with one connection pool from `DATABASE_URL`.
- One session and one transaction per request, shared by all modules while the Backend is a monolith. Why: see [Tradeoffs](#shared-session-in-the-monolith).
  - `modules/main` opens the session of the request with the `DbSession` dependency and passes it to every service call of the request.
  - The transaction is committed when the endpoint returns, before the response is sent. An error in the request rolls it back, so the changes of all modules in the request are saved together or not at all.
  - Service functions take the session as the first argument and never commit or open their own session. They return Pydantic schemas, never ORM objects.
  - Slow external calls (LLM, embeddings) run before the database work of the request, so the request does not hold a connection while it waits.
  - Exception: `POST /api/phones` opens its transaction with `run_in_transaction` from `core/database.py` instead of `DbSession`: see [Transaction retry](#transaction-retry).
- Each module keeps its tables on its own declarative Base (`UsersBase`): no foreign keys between modules, see [SCHEMAS.md](SCHEMAS.md#migrations).
- `core` contains infrastructure only, no domain logic.

## Transaction retry

Applied to `POST /api/phones`: the listing and its search index record ([RAG.md](../ai/RAG.md#indexing)).

- `run_in_transaction(work, attempts=2)` in `core/database.py` opens a session, runs `work(session)` and commits. The commit is a part of the attempt, so a failed commit is retried too.
- A transient database error rolls back the attempt, and `work` runs once more in a new session: 2 attempts in total.
- Transient errors: a lost connection (`connection_invalidated`), `serialization_failure` (SQLSTATE `40001`), `deadlock_detected` (`40P01`). Other errors (integrity, data) are not retried.
- The Guardrail LLM call and the embedding run once, before the first attempt. The second attempt reuses their results: no repeated LLM call and no extra cost.
- After 2 failed attempts nothing is saved and the endpoint returns HTTP 503. The user sends the form again: see [MY_LISTING.md](../features/MY_LISTING.md#add-phone-flow).
- Limitation: see [Tradeoffs](#transaction-retry-without-idempotency).

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

### Transaction retry without idempotency

- A commit that succeeded on the server but lost its acknowledgement is retried and creates a second listing. Accepted for v1.0: the case is rare, and the seller deletes the duplicate.
- Rejected for v1.0: an `Idempotency-Key` header with a table of processed keys. It adds a table and a check to every create request: see [ROADMAP.md](../ROADMAP.md#production-baseline).
- Rejected: a savepoint (`begin_nested`) per attempt. A lost connection breaks the whole transaction, a savepoint does not recover it.
- Rejected: a retry on the Frontend only. It repeats the Guardrail LLM call and the embedding, so a database error doubles the cost of the request.
