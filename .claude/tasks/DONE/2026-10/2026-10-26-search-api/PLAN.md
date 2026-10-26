# PLAN — 2026-10-26-search-api

## v1
plan_version: 1

### Steps
- P1 (R6): `modules/rag/config.py`: `search_model`, `rerank_model`, `guardrail_model`, `rerank_threshold` (0..1). `rag/pyproject.toml` + root lock: `langgraph`, `langchain-openai` for `rag`. `.env.example`: new optional variables.
- P2 (R2, R3, R4): `modules/rag/schemas/search.py`: `SearchRequest` (prompt 1..1000 after trim, extra forbid), `ParsedPrompt` (filters, preferences, model_ids normalized as `ModelCode` format, query_for_embedding), `GuardrailVerdict`, `RerankOutput` (relevance 0..1), `Candidate` (search_index fields of RERANKING.md#input + source path + distance). `PromptBlocked` exception in `schemas` (imported by `main`).
- P3 (R3, R4): `modules/rag/prompts.py`: `GUARDRAIL_SYSTEM`, `PARSE_SYSTEM` (US model codes, same rule as `phones` description prompt), `RERANK_SYSTEM`; prompt and listings inside delimiters.
- P4 (R2): `services/crud.py`: `find_by_model_codes(session, codes, filters, limit=40)`, `find_by_vector(session, embedding, filters, exclude_ids, limit=20)`: one SQL each, `WHERE` only for set filters, `ORDER BY embedding <=> :q`.
- P5 (R4): `modules/rag/ranking.py` (pure, no I/O): `validate_rerank` (unknown and repeated IDs, missing score 0), `apply_threshold`, `order` (relevance, then condition preference only when condition not in filters, then price), `diversity_limit` (5 per `model_code`, moved after, skipped for one `model_id`), `fallback_order` (model code results first, then pgvector by distance, condition preference). Top 20.
- P6 (R2, R5): `modules/rag/graph.py`: `StateGraph` nodes `guardrail -> parse -> retrieve_by_code -> (count < 20 ? retrieve_by_vector) -> merge -> rerank -> END`. State: prompt, parsed, candidates, result ids. `RetryPolicy(max_attempts=2, retry_on=INVALID_LLM_OUTPUT)` on `guardrail`, `parse`; none on `rerank` (its errors caught -> fallback, logged). Session passed through graph config, not state. Embedding of `query_for_embedding` via existing `get_embeddings`. Chat models via `lru_cache` getters in `services/ai.py`. Graph compiled once.
- P7 (R1, R2): `services/__init__.py`: export `search(session, prompt) -> list[UUID]`. `phones/services/crud.py`: `get_phones(session, ids) -> list[PhoneRead]` in given order, missing skipped.
- P8 (R1, R6): `modules/main/routers/search.py`: `POST /search`, `search_rate_limit = RateLimit(3, 10)`, `PromptBlocked` -> 422 generic detail, `AI_ERRORS` and `DBAPIError` -> 503 logged, response `SearchResponse` `{"results": [PhoneRead]}` in `phones.schemas` (see Risks). Include router in `app.py`; `check_config` unchanged (rag errors already collected).
- P9 (A2): tests. `conftest.py`: `AiStubs` gains `search_guardrail`, `parse`, `rerank` stubs, monkeypatched getters. `rag/tests/test_ranking.py` (pure rules), `rag/tests/test_search.py` (graph against PostgreSQL: SQL filters both paths, vector path trigger, dedup, retry on invalid parse, rerank fallback), `main/tests/test_search.py` (HTTP: 200 order and fields, 422 block and body, 503 guardrail and parse failure, 429 4th request). Existing tests with >3 searches override `search_rate_limit` (none expected).
- P10 (R7, A3): `stores/searchStore.ts` keeps `errorText` by status (422, 429, other) from texts in `config/app.ts`; `SearchResults` shows it; prompt kept (already in store). `SearchPage.test.tsx`: three error texts and the prompt in the field.
- P11 (R8): `rag/CLAUDE.md`: search graph, files `graph.py`, `ranking.py`, `prompts.py`, stub fixtures. `main/CLAUDE.md`: `routers/search.py`. docs/backend/STRUCTURE.md: `search.py` in routers list, `rag` internal files. RAG.md#module-interface check against exports.
- P12 (A1-A4): `ruff`, `pytest`, `uv lock --check`, `pnpm lint typecheck test build`, anchor check.

### Order
P1 -> P2 -> P3 -> P4 -> P5 -> P6 -> P7 -> P8 -> P9 -> P10 -> P11 -> P12.

### Risks
- Response wrapper ownership: `main` has no schemas, `rag` cannot import `phones`: `SearchResponse` lives in `phones.schemas` (P8). Alternative for Engineer: a schema in `rag` returning `search_index` copies (no `created_at`, frontend schema breaks). Chosen: `phones.schemas`.
- `DbSession` holds a connection from the first retrieval query to the end of the request, including the rerank LLM call. Accepted for v1.0; the guardrail and parse calls run before any query.
- Model code path may return 20+ listings that the threshold removes: fewer than 20 results (RERANKING.md#one-reranking-call).
- Up to 3 LLM calls and 1 embedding per search: latency; measured later by `make eval`.
- `uv lock` on the device needs network to PyPI for `langgraph`.

## v2
plan_version: 2
change: Engineer feedback: cross-module schemas in root `backend/schemas/` (docs/backend/STRUCTURE.md#folders updated). Only P8, P11 and Risks change, other steps as in v1.

### Steps
- P8 (R1, R6): as v1, but `SearchResponse` `{"results": [PhoneRead]}` in `backend/schemas/search.py` (imports `phones.schemas.PhoneRead`), re-exported by `backend/schemas/__init__.py`. `phones.schemas` unchanged.
- P11 (R8): as v1, plus `main/CLAUDE.md`: response bodies come from module schemas or root `schemas/`.

### Risks
- Replaces v1 risk "Response wrapper ownership": resolved by root `schemas/`. Other v1 risks unchanged.
