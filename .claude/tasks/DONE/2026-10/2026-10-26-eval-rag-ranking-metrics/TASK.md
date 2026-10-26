# TASK — 2026-10-26-eval-rag-ranking-metrics
owner: Engineer
immutable: true

## Requirements
- R1: Step `rag.ranking` per docs/ai/EVALUATION.md#ranking: cases with `relevant` / `highly_relevant` rules over the seed, expected grades by `model_code`, target = `rag.services.search` on the test database, metrics Hit Rate@5, Precision@5, Recall@20, MRR, NDCG@10 as own functions.
- R2: Test database per docs/ai/EVALUATION.md#test-database and docs/backend/DESIGN.md#configuration: `TEST_DATABASE_URL` with the documented default, shared with `conftest.py`; migrations and `seed-reset` before a run with `rag.ranking`; seed embeddings not traced.
- R3: `make eval LOCAL=1` per docs/ai/EVALUATION.md#run: same cases and metrics without LangSmith, same table without tokens and cost, `OPENAI_API_KEY` only.
- R4: Score column = mean per metric (0 to 1) for all datasets per docs/ai/EVALUATION.md#datasets.
- R5: Layout per docs/backend/STRUCTURE.md#eval (`rag/ranking.py`, `database.py`).

## Acceptance
- A1: `ruff check`, `ruff format --check` pass. DB-free tests pass (`eval/tests`, tracing tests).
- A2: Metric unit tests with values computed by hand: the example of docs (NDCG 0.78), no results, no relevant listing found, relevant listings below the cut-off, fewer results than `k`, graded NDCG order.
- A3: Case tests: 10 to 20 cases; every case has 1 to 19 relevant listings; `highly_relevant` is a subset of `relevant`; no rule uses only price and condition.
- A4: Local runner test with a stub target: metrics applied, table printed, no LangSmith client created.
- A5: All Markdown anchor links changed by the task resolve.

## Constraints
- docs/ are already updated and are the source of truth for this task.
- No new dependencies. No change of the search pipeline, prompts or API.
- `make eval` and DB tests are not run by the Validator (no test database here, CLAUDE.md#validator).
