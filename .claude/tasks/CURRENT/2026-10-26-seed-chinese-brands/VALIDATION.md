# VALIDATION — 2026-10-26-seed-chinese-brands

## v1
validation_version: 1
result: PASS

### Checks
- A1: `len(LISTINGS) == 90`, `check_listings()` passes, all listings built as `PhoneCreate`: PASS.
- A2: 7 brands present; new listings: 12 like_new, 12 average, 6 for_repair; users 0-6: PASS.
- A3: no mention of 60 listings left in docs/ and README.md; model code rule in STRUCTURE.md#seed and RAG.md#model-code-limitations: PASS.
- A4: `ruff check` and `ruff format --check` on `backend/seed`: PASS. pytest: not run, every test needs the test database (`TEST_DATABASE_URL`), not reachable from the validation environment; `backend/seed` has no tests.
