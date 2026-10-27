# VALIDATION — 2026-10-26-eval-database

## v1
validation_version: 1
result: FAIL

### Checks
- A1, A2, A4: pass (anchors: only the pre-existing `docs/backend/DESIGN.md` -> `../DESIGN.md#backend`).
- A3: `eval/database.py` reads `TEST_DATABASE_URL` for the guard of R2 (docs/ai/EVALUATION.md#offline-and-online). The intent of A3 (eval never uses the test database) holds; the wording contradicts R2.

### Issues
- I1 (requirement, low): A3 forbids any reference to `TEST_DATABASE_URL` in `eval/`, while R2 requires the guard against it.

## v2
validation_version: 2
result: PASS

### Checks
- I1: A3 reworded by the Engineer. `eval/` uses `TEST_DATABASE_URL` only in the guard (`use_eval_database`); every connection uses `EVAL_DATABASE_URL`.
- A1-A4 pass. Not run here: `make eval` against PostgreSQL.
