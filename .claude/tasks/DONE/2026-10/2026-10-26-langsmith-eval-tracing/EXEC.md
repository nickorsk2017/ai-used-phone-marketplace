# EXEC — 2026-10-26-langsmith-eval-tracing

## v1
exec_version: 1

### Changes
- P1: `core/tracing.py` (`TracingSettings`, `config_errors`, `configure_tracing(force)`; key check is a field validator so the error names `LANGSMITH_API_KEY`); `modules/main/app.py` (`check_config` + `configure_tracing()` in `create_app`); `langsmith>=0.14` in `backend`, `phones`, `rag` pyproject; `uv.lock`; `.env.example`.
- P2: `conftest.py`: `LANGSMITH_TRACING=false`, `LANGCHAIN_TRACING_V2=false`; `TraceCapture` (in-memory LangSmith client for tests). `test_config.py`: `no_env` covers `TracingSettings`.
- P3: `traceable` root runs `phones.description`, `phones.guardrail`, `rag.embed_listing`, `rag.parse`; `graph.run` config `run_name=rag.search`, `tags=["rag"]`.
- P4: `graph._mark_rerank_fallback`: `rerank_fallback`, `rerank_error` on the `rerank` span via `get_current_run_tree()` (verified: returns the node run in LangGraph 1.2; plan fallback not needed).
- P5: `rag.services.parse_prompt` via `llm_call`, re-exported.
- P6: `backend/eval/`: `schemas.py`, `datasets/` (parse 15, clarification 16, description 15 from seed, hallucinated_models 10), `targets.py`, `evaluators.py`, `upload.py` (example comparison instead of a hash: `Client` has no dataset metadata update), `run.py`.
- P7: `Makefile` `eval` target + help; `testpaths` adds `eval`.
- P8: tests: `main/tests/test_tracing_config.py` (6), `phones/tests/test_tracing.py` (3), `rag/tests/test_tracing.py` (8), `eval/tests/` (33). All without database.
- P9: `rag/CLAUDE.md`, `phones/CLAUDE.md`.

### Docs corrected during execution (reported to Engineer)
- EVALUATION.md#tracing: embeddings have no token usage in LangChain traces: latency only, listing cost without the embedding.
- STRUCTURE.md#eval: `schemas.py`, `upload.py` listed; `eval` also reads `phones`/`rag` settings for the model names in the experiment metadata.

### Checks
- `ruff check .`, `ruff format --check .`: pass. `uv lock --check`: pass. `pytest --collect-only`: 237 tests.
- DB-free run (`pytest --noconftest`): new tests 50 passed; `test_config.py`, `test_ranking.py`, `test_guardrails.py` 33 passed.
- DB tests not run in this environment (no PostgreSQL, Engineer decision in chat): `make backend-test` by the Engineer.

## v2
exec_version: 2
change: I1. docs/ai/EVALUATION.md#tracing: `rag.parse` row in the root runs table. No code change.
