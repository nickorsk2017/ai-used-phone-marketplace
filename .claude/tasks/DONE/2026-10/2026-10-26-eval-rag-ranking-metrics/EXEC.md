# EXEC — 2026-10-26-eval-rag-ranking-metrics

## v1
exec_version: 1

### Changes
- P1: `core/config.py`: `TEST_DATABASE_URL_DEFAULT`, `test_database_url()`; `conftest.py` uses it.
- P2: `eval/database.py`: `use_test_database()` (guard `WorkingDatabaseError` when the test URL is the `DATABASE_URL` database; no guard needed when `DATABASE_URL` is not set), `migrate()` (alembic subprocess), `prepare_test_database()` (seed reset with tracing off).
- P3: `eval/rag/ranking.py`: 15 cases (1 to 14 relevant listings each), target on `transaction()` + `search` + `get_phones`, `hit_rate`, `precision`, `recall`, `reciprocal_rank`, `ndcg` and the 5 metric wrappers.
- P4: `EvalDataset.needs_database`; `rag/__init__.py` adds `ranking`.
- P5: `run.py`: `--local` (`run_local`, `apply_metric`), test database preparation, engine disposed only when created, Score = mean with 2 decimals, `rerank_model` in the metadata. `Makefile`: `LOCAL=1`.
- P6: tests `eval/tests/test_ranking.py` (40), `test_run.py` (8), `test_database.py` (4), `test_datasets.py` names.

### Deviation (reported to Engineer)
- `Makefile` `eval` no longer depends on `backend-check`: it requires `DATABASE_URL` and `SESSION_SECRET`, while docs/ai/EVALUATION.md#run says `make eval LOCAL=1` needs `OPENAI_API_KEY` only. `run.py` checks the settings of `phones` and `rag` itself.
- A manual check of `python -m eval.run --local --dataset rag.parse` ran with the real `OPENAI_API_KEY` of `backend/.env` (up to about 30 OpenAI calls) and failed at the engine dispose with an invalid `DATABASE_URL`: fixed (dispose only a created engine).

### Checks
- `ruff check`, `ruff format --check`: pass. DB-free pytest (eval + tracing): 105 passed. `pytest --collect-only`: 292.
