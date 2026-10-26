# VALIDATION — 2026-10-26-phones-guardrails-rate-limit

## v1
validation_version: 1
result: PASS

### Checks
- A1: `ruff check`, `ruff format --check`, `pytest` 147 passed (PostgreSQL 16, pgvector 0.8.1): PASS.
- A2: uppercase conversion, invalid `model_code` 422 before the LLM, `model_code` in Regex and in the LLM message, 429 + `Retry-After` on both phones endpoints, independent counters, my-listings 3/10 s (docs/INFRA.md#application supersedes TASK.md R3 "not limited", PLAN v2): PASS.
- A3: `pnpm lint`, `typecheck`, `test` 86 passed, `build`; 429 texts per docs/features/MY_LISTING.md: PASS.
- A4: 0 broken anchors in `docs/`, `README.md`, `CLAUDE.md`, `backend/modules/*/CLAUDE.md`: PASS.
- docs/ai/RAG.md#module-interface matches `rag.service.embed_listing` and `index`: PASS.
- frontend/CLAUDE.md: static texts in JSX, memoized blocks, files under 200 lines: PASS.
- `make eval`: not run, per CLAUDE.md#validator.

### Notes
- With React Strict Mode in development the page load can call `GET /api/my-listings` twice; with the reload after publish this is 3 requests and fits the limit.
