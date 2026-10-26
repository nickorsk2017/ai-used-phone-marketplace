# VALIDATION — 2026-10-26-eval-rag-ranking-metrics

## v1
validation_version: 1
result: PASS

### Checks
- A1: ruff pass; 105 DB-free tests pass.
- A2: hand-computed values: docs example (NDCG 0.78), no results, nothing found, below the cut-off, fewer than `k`, graded order.
- A3: 15 cases; 1 to 14 relevant listings each; `highly_relevant` applied on relevant listings only (subset by construction); every rule selects by more than price and condition.
- A4: local runner with a stub target; `Client` replaced by a failing stub and never called.
- A5: changed anchors resolve; only the pre-existing `docs/backend/DESIGN.md` -> `../DESIGN.md#backend` remains (reported).
- docs vs code: EVALUATION.md#ranking, #test-database, #metrics, #run, backend/DESIGN.md#configuration, STRUCTURE.md#eval match. Makefile deviation documented in EXEC, consistent with EVALUATION.md#run.
- Not run here: `make backend-test` and `make eval` (no PostgreSQL; real keys).
