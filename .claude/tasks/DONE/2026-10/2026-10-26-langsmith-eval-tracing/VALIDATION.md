# VALIDATION — 2026-10-26-langsmith-eval-tracing

## v1
validation_version: 1
result: FAIL

### Checks
- A1: `ruff check`, `ruff format --check`: pass. `make backend-test` with PostgreSQL: not run here (Engineer decision, no test database); DB-free tests pass.
- A2: pass (`test_tracing_config.py`, `phones/tests/test_tracing.py`, `rag/tests/test_tracing.py`).
- A3: pass (`eval/tests`, 33).
- A4: changed links resolve. Pre-existing, outside the task: `docs/backend/DESIGN.md` links `../DESIGN.md#backend`, file `docs/DESIGN.md` does not exist (in HEAD before the task). Reported to Engineer, not blocking.
- docs vs code: R1-R6 match docs, except I1.

### Issues
- I1 (logic, low): `rag.parse` is a root run in code (`parse_prompt`), missing in the root runs table of docs/ai/EVALUATION.md#tracing.

## v2
validation_version: 2
result: PASS

### Checks
- I1: fixed, `rag.parse` in docs/ai/EVALUATION.md#tracing matches `parse_prompt`.
- A1-A4 as v1: ruff pass, 50 DB-free tests pass, anchors resolve except the pre-existing `docs/backend/DESIGN.md` -> `../DESIGN.md#backend` (outside the task, reported).
- Open for the Engineer: `make backend-test` with PostgreSQL; `make eval` with real keys (CLAUDE.md#validator).
