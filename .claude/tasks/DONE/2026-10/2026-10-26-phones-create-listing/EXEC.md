# EXEC — 2026-10-26-phones-create-listing

## v1
exec_version: 1

### Summary
- P1: `core/database.py`: `is_transient_error`, `run_in_transaction(work, attempts=2)`.
- P2: `modules/rag`: `RagBase`, `SearchIndex` (`vector(1536)`, HNSW cosine), `IndexedPhone`, `service.embedding_input/embed_listing/index`. Workspace member added.
- P3: `modules/phones`: `PhonesBase`, `Phone`, schemas `PhoneDescriptionRequest`, `PhoneDescription`, `PhoneCreate`, `PhoneRead`, `MyListings`, `GuardrailVerdict`, `GeneratedDescription`; `service.create_phone/list_user_phones`. `langchain-openai` moved from `phones` to `main` (clients are created in `main`).
- P4: `prompts.py`, `service.generate_description` (`_structured_call`: one repeat on `ValidationError` / `OutputParserException`).
- P5: `guardrails.py` (port of `frontend/utils/guardrails.ts`), `service.check_listing` (regex, then LLM).
- P6: `migrations/versions/0002_create_phones_and_search_index.py`, `migrations/env.py` collects the 3 Bases.
- P7: `main/config.py` (`OPENAI_API_KEY` required, 3 models), `main/ai.py`, `routers/phones.py`, `routers/my_listings.py`, `app.py`, `backend/.env.example`.
- P8: `backend/conftest.py` (`app` fixture, `StubChatModel`, `StubEmbeddings`, truncate of the new tables, `OPENAI_API_KEY`); tests in `phones/tests`, `rag/tests`, `main/tests/test_transaction_retry.py`, `main/tests/test_phones.py`, `main/tests/test_config.py`.
- P9: `frontend/stores/myListingsStore.ts`: `add` reloads `GET /api/my-listings` (fallback: local prepend when the reload fails). `AddPhoneModal.test.tsx`: reload asserted, 422 rejection case.
- P10: `backend/modules/phones/CLAUDE.md`, `backend/modules/rag/CLAUDE.md`, `backend/modules/main/CLAUDE.md`.
- P11: `ruff check`, `ruff format --check`, `pytest` 132 passed (PostgreSQL 16 + pgvector 0.8.1); `alembic downgrade base / upgrade head / check / downgrade base / upgrade head`; `uv lock --check`; `pnpm lint`, `typecheck`, `test` 84 passed, `build`; anchor check 0 broken.

### Changed files
- backend/core/database.py
- backend/conftest.py, backend/.env.example, backend/pyproject.toml, backend/uv.lock
- backend/migrations/env.py, backend/migrations/versions/0002_create_phones_and_search_index.py
- backend/modules/rag/{__init__.py, pyproject.toml, database.py, service.py, CLAUDE.md, models/*, schemas/*, tests/*}
- backend/modules/phones/{pyproject.toml, database.py, service.py, guardrails.py, prompts.py, CLAUDE.md, models/*, schemas/*, tests/*}
- backend/modules/main/{pyproject.toml, config.py, ai.py, app.py, CLAUDE.md, routers/phones.py, routers/my_listings.py, tests/test_config.py, tests/test_phones.py, tests/test_transaction_retry.py}
- frontend/stores/myListingsStore.ts, frontend/features/__test__/my-listings/AddPhoneModal.test.tsx

### Notes
- `POST /api/phones`: `CurrentUser` still opens the request session (`DbSession`) for authentication; it stays open during the LLM calls (PLAN risk 1).
- No real OpenAI call was made: no key in the environment.

## v2
exec_version: 2

### Summary
- L1: `modules/main/dependencies.py`: `get_current_user_short_session` / `CurrentUserShortSession` authenticates in its own `run_in_transaction`, closed before the endpoint; shared 401 / cookie logic in `_session_user`. `routers/phones.py`: both endpoints on `CurrentUserShortSession`. Test `test_no_connection_is_held_during_the_llm_calls`: pool checked-out connections during the LLM calls = 0 (1 with `CurrentUser`). `modules/main/CLAUDE.md` updated.
- L2: `pydantic-settings` removed from `modules/phones/pyproject.toml`, `uv.lock` updated.
- `ruff check`, `pytest` 133 passed, `uv lock --check`, anchor check 0 broken.

### Changed files
- backend/modules/main/dependencies.py, backend/modules/main/routers/phones.py, backend/modules/main/CLAUDE.md, backend/modules/main/tests/test_phones.py
- backend/modules/phones/pyproject.toml, backend/uv.lock
