# EXEC — 2026-10-26-search-api

## v1
exec_version: 1
plan_version: 2

### Changes
- P1: `rag/config.py` (search, rerank, guardrail models, `rerank_threshold`), `rag/pyproject.toml` (`langchain-openai`, `langgraph` 1.2.17), `uv.lock`, `.env.example`.
- P2: `rag/schemas/search.py` (`SearchRequest`, `SearchGuardrailVerdict`, `ParsedPrompt` with `filters.price.max_value` for ranges, `Candidate`, `RerankOutput`, `PromptBlocked`), re-exported in `rag/schemas/__init__.py`.
- P3: `rag/prompts.py`.
- P4: `rag/services/crud.py`: `filter_conditions`, `find_by_model_codes` (limit 40), `find_by_vector` (cosine, exclude code results, limit 20).
- P5: `rag/ranking.py`: `merge`, `validate_scores`, `rank`, `fallback_order`, `diversity_limit`, `top`.
- P6: `rag/graph.py`: 6 nodes, conditional edge `needs_vector`, `RetryPolicy` (2 attempts, validation errors, no wait) on `guardrail` and `parse`; rerank errors -> fallback, logged. `rag/services/ai.py`: chat model getters, `embed_query`, `structured_call` (one attempt).
- P7: `rag/services/search.py` + export; `phones/services/crud.py` `get_phones` + export.
- P8: `backend/schemas/search.py` `SearchResponse`; `main/routers/search.py`; `search_rate_limit` 3/10 s; router in `app.py`.
- P9: `conftest.py` stubs `search_guardrail`, `search_parse`, `rerank`; `rag/tests/test_ranking.py`, `rag/tests/test_search.py`, `main/tests/test_search.py`.
- P10: `searchStore.ts` (`error`), `SearchResults.tsx` (texts of SEARCH_PAGE.md#errors), `SearchPage.tsx`, `SearchPage.test.tsx` (422, 429).
- P11: `rag/CLAUDE.md`, `main/CLAUDE.md`, docs/backend/STRUCTURE.md.
- Side fix: import order in `phones/services/ai.py` (ruff I001, pre-existing).

### Checks
- P12: `ruff check`, `ruff format --check`, `uv lock --check` pass; `pytest` 184 passed; `pnpm lint`, `typecheck`, `test` (87), `build` pass; anchors 0 broken. Run in a cloud copy with PostgreSQL 16 + pgvector.
