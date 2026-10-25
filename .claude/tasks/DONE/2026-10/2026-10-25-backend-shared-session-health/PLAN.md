# PLAN — 2026-10-25-backend-shared-session-health

## v1
plan_version: 1

### Steps
- P1 (R3): DESIGN.md#database-connection: request session and transaction owned by `modules/main`, services take the session as the first argument and never commit; Tradeoffs: shared session only while modules share one database. API.md: health row. auth/CLAUDE.md: module boundary rule replaced. main/CLAUDE.md: `DbSession`, `routers/health.py`.
- P2 (R1): `core/database.py`: request transaction (session + `begin`: commit on success, rollback on error). `get_session` removed (no callers).
- P3 (R1): `modules/main/dependencies.py`: `DbSession` with `Depends(..., scope="function")` (FastAPI 0.162: exit code runs before the response is sent, so a failed commit is a 500, not a lost write). `owner_access` loads with the request session.
- P4 (R1): `modules/auth/service.py`: `session` first argument, no `commit`, no own session. `routers/users.py` passes `DbSession`.
- P5 (R2): `core/database.py`: database probe `SELECT 1` with a timeout, returns availability, never raises. `routers/health.py`: 200 / 503, no rate limit, no request session. `app.py` includes it.
- P6 (A1-A3): `conftest.py` session fixture for service tests. Tests: one session per request, rollback on error, health 200/503. ruff, format, pytest, alembic check.

### Risks
- A long request holds a connection for the whole request. LLM calls inside a transaction (phones) hold it during the LLM call: for `modules/phones` the LLM call must run before the database work. Noted in DESIGN.md Tradeoffs.
- Supabase transaction pooler: one transaction per request fits its mode.
