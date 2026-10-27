# PLAN — 2026-10-26-eval-database

## v1
plan_version: 1

### Steps
- P1 (R1): `core/config.py`: `EVAL_DATABASE_URL_DEFAULT`, `eval_database_url()` next to the test URL.
- P2 (R2): `eval/database.py` `use_eval_database()`: compares the normalized eval URL with `DATABASE_URL` (when configured) and `test_database_url()`; raises `WorkingDatabaseError` naming the clashing variable; then points `DATABASE_URL` of the process to the eval URL.
- P3 (R3): `ensure_database(url)`: asyncpg connection to the `postgres` maintenance database of the same server, `CREATE DATABASE` when `pg_database` has no row; a clear error when creation is refused. `seed_fingerprint()`: sha256 of the JSON of `USERS`, `LISTINGS`, the rag `embedding_model` and the sorted names of `migrations/versions/*.py`. `read_fingerprint()` / `write_fingerprint()`: `shobj_description` of the current database / `COMMENT ON DATABASE` (identifier quoted), on the shared engine. `prepare_eval_database()`: guard -> ensure -> migrate -> compare -> seed reload with tracing off + write, or skip with a message. Comment read error -> reload; write error -> warning, run continues.
- P4: `run.py` calls `prepare_eval_database()`; `ranking.py` docstring links the new section.
- P5 (A2, A3): `eval/tests/test_database.py`: guard, defaults, fingerprint, reload decision with stubbed `ensure_database`, `migrate`, `read_fingerprint`, `write_fingerprint`, `load_seed` (no database).
- P6 (A1, A4): ruff, DB-free pytest, anchors.

### Order
P1 -> P2 -> P3 -> P4 -> P5 -> P6.

### Risks
- `COMMENT ON DATABASE` needs ownership: the auto-created database is owned by the user; otherwise a warning and a reload on every run (the previous behaviour).
- `CREATE DATABASE` refused on managed PostgreSQL: documented manual creation.
