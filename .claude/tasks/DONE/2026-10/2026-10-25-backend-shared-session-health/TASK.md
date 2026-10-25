# TASK — 2026-10-25-backend-shared-session-health
owner: Engineer
immutable: true

## Requirements
- R1: One database session per request, shared by all modules while the Backend is a monolith. One transaction per request: commit when the endpoint succeeds, rollback on an error, before the response is sent. Module services use the session of the request and do not commit. Enables one transaction across modules (docs/ai/RAG.md#indexing).
- R2: `GET /api/health` checks the database connection: 200 `{"status": "ok"}` when the database answers, 503 with an error when it does not or does not answer in time.
- R3: docs/ updated before the code (CLAUDE.md#1): docs/backend/DESIGN.md#database-connection (session and transaction, Tradeoffs), docs/backend/API.md (health), backend/modules/auth/CLAUDE.md and backend/modules/main/CLAUDE.md (module boundary, session dependency, health router).

## Acceptance
- A1: `ruff check`, `ruff format --check`, `pytest` and `alembic check` pass against PostgreSQL.
- A2: Tests: the Owner dependency and the endpoint use one session per request; an error after a write in a request rolls the write back; existing user tests pass.
- A3: Tests: health 200 with a database, 503 when the database is unavailable; health is not rate limited.

## Constraints
- No new dependencies. Out of scope: `modules/phones`, `modules/rag`, Frontend.
