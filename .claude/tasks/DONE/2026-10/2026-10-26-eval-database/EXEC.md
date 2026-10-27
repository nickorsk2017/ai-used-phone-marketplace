# EXEC — 2026-10-26-eval-database

## v1
exec_version: 1

### Changes
- P1: `core/config.py`: `EVAL_DATABASE_URL_DEFAULT`, `eval_database_url()`.
- P2: `eval/database.py` `use_eval_database()`: guard against `DATABASE_URL` and `TEST_DATABASE_URL` (normalized), error names the variable.
- P3: `ensure_database` (asyncpg, maintenance database `postgres`, quoted `CREATE DATABASE`), `migrate`, `seed_fingerprint` (`seed:` + sha256 of users, listings, embedding model, migration names), `read_fingerprint` / `write_fingerprint` (database comment, format checked before the literal), `prepare_eval_database` (skip on match; reload + write otherwise; read error -> reload; write error -> message).
- P4: `run.py` -> `prepare_eval_database`; `ranking.py`, `schemas.py` links to EVALUATION.md#evaluation-database.
- P5: `eval/tests/test_database.py` (16): guard, defaults, fingerprint, reload decision with stubs, guard before any step.

### Checks
- ruff pass; DB-free pytest: eval 98, eval + tracing 115.
