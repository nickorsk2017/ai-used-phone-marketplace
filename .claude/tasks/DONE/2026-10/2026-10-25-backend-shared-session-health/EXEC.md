# EXEC — 2026-10-25-backend-shared-session-health

## v1
exec_version: 1

### Summary
- P1: DESIGN.md#database-connection (request session and transaction, services take the session, slow calls before database work) + `## Tradeoffs` (shared session in the monolith). API.md: `GET /api/health`. auth/CLAUDE.md, main/CLAUDE.md: module boundary, `DbSession`, `routers/health.py`.
- P2: `core.database.transaction()` (session + `begin`). `get_session` removed.
- P3: `DbSession = Depends(transaction, scope="function")`. `owner_access` loads with the request session.
- P4: `auth.service` functions take `session` first, no commit. `users` router passes `DbSession`.
- P5: `core.database.is_database_available` (`SELECT 1`, `asyncio.timeout` 2s). `routers/health.py` 200 / 503 `Database is unavailable`. Health removed from `app.py`.
- P6: `session` fixture. `test_session.py` (shared session, rollback on error, commit), `test_health.py` (200, 503, timeout). ruff, format, pytest 47/47, alembic check on PostgreSQL 16: PASS.

### Changed files
- docs/backend/{DESIGN.md, API.md}
- backend/conftest.py, backend/core/database.py
- backend/modules/auth/{CLAUDE.md, service.py, tests/test_service.py}
- backend/modules/main/{CLAUDE.md, app.py, dependencies.py, routers/users.py, routers/health.py, tests/test_session.py, tests/test_health.py, tests/test_users.py}
