# TASK — 2026-10-26-search-api
owner: Engineer
immutable: true

## Requirements
- R1: `POST /api/search` per docs/backend/API.md#search: body, 200 response with listings in rank order, 422, 429, 503.
- R2: Search pipeline in `modules/rag` per docs/ai/RAG.md#architecture as a LangGraph graph (docs/ai/RAG.md#orchestration-langgraph): Guardrail 2, prompt parsing (docs/ai/RAG.md#llm-output-structure), model code retrieval, pgvector retrieval when fewer than 20 listings, merge and deduplication, reranking. Condition and price filters in SQL on both paths (docs/ai/RAG.md#search-index-table, docs/features/SEARCH_PAGE.md#condition-and-price).
- R3: Guardrail 2 per docs/ai/GUARDRAILS.md#guardrail-2-search-prompt, fail closed.
- R4: Reranking per docs/ai/RERANKING.md: input, output validation, threshold, ranking rules, diversity limit, fallback without HTTP 503.
- R5: Errors and retries per docs/ai/RAG.md#errors-and-retries: client retry, one repeated LLM node call on a validation error (LangGraph `RetryPolicy`).
- R6: Settings of `modules/rag` per docs/backend/DESIGN.md#configuration. Rate limit per docs/INFRA.md#application.
- R7: Frontend per docs/features/SEARCH_PAGE.md#errors: texts for 422, 429 and other errors, the prompt stays in the field.
- R8: `backend/modules/rag/CLAUDE.md`, `backend/modules/main/CLAUDE.md` and docs/backend/STRUCTURE.md describe the new files where needed. docs/ai/RAG.md#module-interface matches `rag.services`.

## Acceptance
- A1: `make backend-test` passes. `ruff check`, `ruff format --check`, `uv lock --check` pass.
- A2: Backend tests with stub LLM and embeddings: filters applied in SQL on both paths (no result violates price or condition), pgvector path only when fewer than 20 model code listings, deduplication by `phone_id`, reranker IDs outside the candidates and repeats removed, threshold applied, diversity limit 5 per `model_code` and not applied for one model, fallback order on reranker failure, Guardrail 2 block 422 and failure 503, parsing failure 503, one repeated call on an invalid parsing output, 429 on the 4th request within 10 s, response in rank order with the fields of `GET /api/phones/{id}`.
- A3: Frontend `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build` pass. Tests: 422, 429 and other error texts, prompt kept.
- A4: All Markdown anchor links in `docs/`, `CLAUDE.md` and `backend/modules/*/CLAUDE.md` resolve.

## Constraints
- docs/ are already updated for this task and are the source of truth (API.md#search, INFRA.md#application, DESIGN.md#configuration, RAG.md#module-interface, GUARDRAILS.md#guardrail-2-search-prompt, SEARCH_PAGE.md#errors).
- No real OpenAI calls in tests. `make eval` is not run (CLAUDE.md#validator).
- Out of scope: listing update and delete with reindexing, `rag.delete`, LangSmith and DeepEval setup, `GET /api/phones/{id}/contact` rate limit.
