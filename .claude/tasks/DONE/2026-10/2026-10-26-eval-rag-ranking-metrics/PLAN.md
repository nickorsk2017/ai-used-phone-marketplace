# PLAN — 2026-10-26-eval-rag-ranking-metrics

## v1
plan_version: 1

### Steps
- P1 (R2): `core/config.py`: `TEST_DATABASE_URL_DEFAULT` and `test_database_url()` (environment only). `conftest.py` uses it instead of its own literal.
- P2 (R2, R5): `eval/database.py`: `prepare_test_database()`: sets `DATABASE_URL` of the process to the test URL before the first engine is created, runs `alembic upgrade head` in a subprocess with that URL, then `seed.run.main(reset=True)` inside `tracing_context(enabled=False)`. Refuses to run when the test URL equals the configured `DATABASE_URL` (guard against the working database).
- P3 (R1): `eval/rag/ranking.py`:
  - `RankingCase` (dataclass: prompt, `relevant`, `highly_relevant` predicates over `PhoneCreate`), `example()` computes `{"grades": {model_code: 1|2}}` from `seed.run.LISTINGS`.
  - 15 cases across: battery, camera, display size, brand, model family, foldable, a named model (exact model grade 2, siblings grade 1), compact phones, iOS/Android with a preference, a Spanish prompt. Counts checked against the seed while writing.
  - Pure functions `hit_rate`, `precision`, `recall`, `mrr`, `ndcg` per the formulas of EVALUATION.md#metrics; LangSmith metric wrappers keyed `hit_rate@5`, `precision@5`, `recall@20`, `mrr`, `ndcg@10`.
  - `target`: one `transaction()` per case, `rag.services.search`, then `phones.services.get_phones` for the model codes in order; clarification -> `ranked: []` with `clarification`; `PromptBlocked` -> `ranked: []` with `error`.
  - `DATASET` with `needs_database=True`.
- P4 (R1, R5): `schemas.EvalDataset.needs_database: bool = False`; `rag/__init__.py` adds `ranking.DATASET`.
- P5 (R3, R4): `run.py`: `--local`; selection of datasets; `prepare_test_database()` when a selected dataset needs it; LangSmith path unchanged; local path: `run_local(dataset)` with bounded concurrency (4), timing per case, metrics called with the keyword arguments they declare (`inputs`, `outputs`, `reference_outputs`); both paths fill `DatasetReport`. Scores stored as floats, Score column = mean with 2 decimals. Tracing: `configure_tracing(force=True)` for LangSmith, `configure_tracing()` for local. `Makefile`: `LOCAL=1` -> `--local`.
- P6 (A2-A4): tests: `eval/tests/test_ranking.py` (metrics by hand, cases A3), `test_run.py` (local runner with a stub dataset, no `Client`; mean formatting), `test_database.py` (URL guard, env override, no DB connection).
- P7 (A1, A5): ruff, DB-free pytest, anchor check.

### Order
P1 -> P2 -> P3 -> P4 -> P5 -> P6 -> P7.

### Risks
- Seed reload on every run with `rag.ranking`: 90 embedding calls (cheap, about 10 s with the seed concurrency).
- Case rules depend on the seed data: a seed change can push a case outside 1..19; caught by the A3 test.
- `alembic` in a subprocess inherits the process environment: the test URL is passed explicitly.
- The reranker is an LLM: scores vary between runs (documented).
