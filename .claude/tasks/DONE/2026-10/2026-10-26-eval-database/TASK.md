# TASK — 2026-10-26-eval-database
owner: Engineer
immutable: true

## Requirements
- R1: `EVAL_DATABASE_URL` per docs/backend/DESIGN.md#configuration (environment only, documented default); `TEST_DATABASE_URL` stays for the tests only.
- R2: Guard per docs/ai/EVALUATION.md#offline-and-online: stop before any change when `EVAL_DATABASE_URL` equals `DATABASE_URL` or `TEST_DATABASE_URL`.
- R3: Preparation per docs/ai/EVALUATION.md#evaluation-database: create the database when missing, migrations, seed reload only on a fingerprint change (seed users and listings, embedding model, migration files), fingerprint stored as the database comment, full reload when the comment is missing or unusable; seed embeddings not traced.
- R4: docs/backend/STRUCTURE.md#eval: `eval/database.py`.

## Acceptance
- A1: `ruff check`, `ruff format --check` pass; DB-free tests pass.
- A2: Tests without a database: default URL; guard against `DATABASE_URL` and `TEST_DATABASE_URL` (driver prefixes normalized); fingerprint changes with a listing, the embedding model or a migration file and is stable otherwise; reload decision: matching comment skips the seed, missing or different comment reloads and writes the new fingerprint, a comment error reloads.
- A3: `eval/` never connects to the database of `TEST_DATABASE_URL`: it reads it for the guard of R2 only.
- A4: All Markdown anchor links changed by the task resolve.

## Constraints
- docs/ are already updated and are the source of truth.
- No change of the app schema, the migrations or the seed data.
- `make eval` is not run by the Validator.
