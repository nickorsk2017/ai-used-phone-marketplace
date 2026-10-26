# CLAUDE.md — modules/rag

Rules for AI coding agents working in `backend/modules/rag/`. Project rules: [../../../CLAUDE.md](../../../CLAUDE.md).

## Sources of truth

- Search architecture and the module interface: [docs/ai/RAG.md](../../../docs/ai/RAG.md#module-interface).
- Indexing: [docs/ai/RAG.md](../../../docs/ai/RAG.md#indexing). `search_index` table: [docs/backend/SCHEMAS.md](../../../docs/backend/SCHEMAS.md#search_index-modulesrag).

## Module boundary

- `services/` is the public interface of the module, called by `modules/main` only. `services/__init__.py` re-exports the public functions: `services/ai.py` has the embedding calls, the chat models (`get_guardrail_model`, `get_search_model`, `get_rerank_model`) and `structured_call` used by the graph nodes, `services/crud.py` has the database functions (take the session). Other modules import only `services` and `schemas/`, never `models/` or `database.py`.
- The module does not import `modules/phones`. The listing fields come as `IndexedPhone`.
- `index` runs in the transaction of the listing: it takes the session of the caller and never commits: [docs/backend/DESIGN.md](../../../docs/backend/DESIGN.md#transaction-retry).
- `search(session, prompt)` runs the LangGraph graph of `services/graph.py`, one node per step of [docs/ai/RAG.md](../../../docs/ai/RAG.md#architecture). The session goes in the run config (`configurable.session`), not in the state. `RetryPolicy` on the `guardrail` and `parse` nodes repeats invalid output only; LLM calls in the graph use `services/ai.structured_call` (one attempt), not `core.llm.llm_call`, so the repeat is not doubled. Reranker errors fall back to `services/ranking.fallback_order`: [docs/ai/RERANKING.md](../../../docs/ai/RERANKING.md#errors).
- Internal files: `services/graph.py` (pipeline) and `services/ranking.py` (ranking rules, no I/O), not re-exported by `services/__init__.py`; `prompts/` (system prompts, one file per prompt: `guardrail.py`, `parse.py`, `rerank.py`; `delimiters.py` has the search prompt delimiter shared by `guardrail.py` and `parse.py`; user text inside delimiters); `schemas/search.py` (request, LLM outputs, candidates, `PromptBlocked`).
- The embedding is computed by `embed_listing` before the transaction. Settings: `config.py` ([DESIGN.md](../../../docs/backend/DESIGN.md#configuration)). The embeddings client is created in `services/ai.py` (`get_embeddings`) with `embeddings` of `core/llm.py`. Tests replace it and the chat models (`get_guardrail_model`, `get_search_model`, `get_rerank_model`) with the `ai_stubs` fixture of `backend/conftest.py`.

## Database

- Tables are declared on `RagBase` only. `search_index.phone_id` has no foreign key to `phones`.
- The enum types `phone_os` and `phone_condition` are created by the `phones` table in migration `0002` and reused here by name.

## Tests

- `tests/` runs against PostgreSQL with pgvector from `TEST_DATABASE_URL`. Embeddings are the stubs of `backend/conftest.py`.
