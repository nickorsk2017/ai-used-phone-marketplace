# VALIDATION — 2026-10-26-search-api

## v1
validation_version: 1
exec_version: 1
result: PASS

### Checks
- R1 API.md#search: body limits and extra fields 422, rank order, fields equal `GET /api/phones/{id}`, empty list, 422 without reason, 503, 429 with `Retry-After`: `main/tests/test_search.py`.
- R2 RAG.md#architecture: graph nodes match the diagram; filters in SQL on both paths; vector path only below 20; candidates at most 39 (code < 20 + vector 20) within RERANKING.md#position-in-the-pipeline limit 40; dedup by `phone_id`.
- R3 GUARDRAILS.md#guardrail-2-search-prompt: delimiters, block 422, fail closed 503, parse not called after block.
- R4 RERANKING.md: filters not passed to the reranker, listings in delimiters, unknown/repeated IDs, missing score 0, threshold from settings, condition preference only without condition filter, price tie-break, diversity 5 per code and skipped for one model, fallback order without 503.
- R5 RAG.md#errors-and-retries: client `max_retries=2`; node `RetryPolicy` validation only, 2 attempts, no doubling with `llm_call`.
- R6 DESIGN.md#configuration, INFRA.md#application: settings and 3/10 s limit match.
- R7 SEARCH_PAGE.md#errors: three texts, prompt kept.
- R8: module CLAUDE.md files, STRUCTURE.md (root `schemas/`, `search.py`, rag internal files), RAG.md#module-interface matches `rag.services.__all__`.
- A1-A4: as EXEC v1 checks; anchors 0 broken.

### Issues
- none
