# TASK — 2026-10-26-phones-create-listing
owner: Engineer
immutable: true

## Requirements
- R1: `modules/phones` per docs/backend/DESIGN.md#modules and docs/backend/SCHEMAS.md#phones-modulesphones: `phones` table on `PhonesBase`, models, schemas, `service.py`: create a listing, list the listings of a user (newest first), generate the description (LLM), Guardrail 1 check. Domain module rules per docs/backend/STRUCTURE.md#domain-module, no settings of its own.
- R2: Description generation per docs/features/MY_LISTING.md#description-response: structured LLM output with `model_found`, 422 when not found, one repeated call on a Pydantic validation error per docs/ai/RAG.md#errors-and-retries.
- R3: Guardrail 1 on the Backend per docs/ai/GUARDRAILS.md#guardrail-1-phone-saving: Backend Regex with the rules of `frontend/utils/guardrails.ts`, then the LLM Guardrail. Checked fields, output, 422 without the layer or category, fail closed with 503.
- R4: Minimal `modules/rag` per docs/ai/RAG.md#indexing and docs/backend/SCHEMAS.md#search_index-modulesrag: `search_index` table on `RagBase` with `vector(1536)` and the HNSW cosine index, `service.py`: embedding of the listing text, `index(session, phone, embedding)`.
- R5: Migration `0002_create_phones_and_search_index.py` per docs/backend/SCHEMAS.md#migrations. `migrations/env.py` collects `PhonesBase.metadata` and `RagBase.metadata`.
- R6: `run_in_transaction` in `core/database.py` per docs/backend/DESIGN.md#transaction-retry.
- R7: `modules/main`: settings per docs/backend/DESIGN.md#configuration in the configuration check, `ai.py`, `backend/.env.example` updated. Endpoints per docs/backend/API.md: `POST /api/phones/description`, `POST /api/phones`, `GET /api/my-listings`, access level `User` (`CurrentUser`). `POST /api/phones` order: Regex, LLM Guardrail, embedding, then `run_in_transaction` with `phones` and `search_index`.
- R8: Frontend per docs/features/MY_LISTING.md#add-phone-flow: after a successful `POST /api/phones` the list is loaded again with `GET /api/my-listings`. 422 and 503 texts as in the flow.
- R9: Module rules: new `backend/modules/phones/CLAUDE.md` and `backend/modules/rag/CLAUDE.md`. `backend/modules/main/CLAUDE.md` mentions `ai.py` and `run_in_transaction`.

## Acceptance
- A1: `make backend-test` passes against PostgreSQL with pgvector. `ruff check` passes. No real OpenAI calls in tests: the LangChain clients are replaced by stubs through FastAPI dependency overrides.
- A2: Backend tests: Regex cases (card number with Luhn, phone number, links, clean text), LLM Guardrail blocked and allowed, LLM Guardrail error -> 503 and nothing saved, description found and not found (422), description validation error repeated once, `POST /api/phones` without a session 401, created listing in `phones` and `search_index` with the same id and copied fields, embedding error -> 503 and nothing saved, transient database error on the first attempt -> saved on the second attempt with one embedding call, transient error on both attempts -> 503 and nothing saved, non-transient error not retried, `GET /api/my-listings` returns only own listings, newest first.
- A3: `alembic upgrade head`, `downgrade base`, `upgrade head` work on an empty database. `alembic check` reports no new operations.
- A4: Frontend `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build` pass. Test: after a successful publish `GET /api/my-listings` is requested again.
- A5: All Markdown anchor links in `docs/` and `backend/modules/*/CLAUDE.md` resolve.

## Constraints
- docs/ is already updated and is the source of truth for this task. A discrepancy found during the task is reported, not resolved in code.
- Builds on the closed task `users-auth-cookie-session` (`modules/users`, `CurrentUser`).
- New dependencies: `pgvector` (SQLAlchemy type), LangChain packages already declared in `modules/phones/pyproject.toml`.
- Out of scope: `PATCH`, `DELETE`, `GET /api/phones/{id}`, `GET /api/phones/{id}/contact`, `POST /api/search`, rate limits of the phones endpoints, `Idempotency-Key`, `make eval`.
