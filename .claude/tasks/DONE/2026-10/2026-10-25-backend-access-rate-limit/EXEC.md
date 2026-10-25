# EXEC — 2026-10-25-backend-access-rate-limit

## v1
exec_version: 1

### Summary
- P1: AUTH.md#access (header only for access checks, Owner rule, UUID compare, statuses), API.md (PUT, 429), INFRA.md#application (per-module limits table, in-memory counters, client IP behind Caddy), DESIGN.md#configuration (`.env` path), main/CLAUDE.md (`dependencies.py`, `rate_limit.py`).
- P2: `ENV_FILE` resolved from `__file__` in `core/config.py` and `modules/main/config.py`. Database settings moved from `modules/auth` to `core` by a parallel refactor before execution: R4 applied to `core/config.py`. `test_config.py` disables `.env` through `model_config` instead of `chdir`.
- P3: `UserFields` base, `UserCreate`, `UserUpdate`; `service.update_user` (`UPDATE ... RETURNING`).
- P4: `owner_access[Resource](load, owner_of, path_param, not_found)`: path id parse/load -> 404, header parse + UUID compare -> 403. `OwnedUser`. `ensure_owner` removed.
- P5: `RateLimit` sliding window per client IP, `Retry-After`, sweep of stale clients once per window, `reset_all`. `auth_rate_limit` 5/10s on the `users` router.
- P6: GET returns `OwnedUser`, PUT updates it.
- P7: `reset_rate_limits` autouse fixture. ruff, ruff format, pytest 42/42, `alembic check` on PostgreSQL 16: PASS.

### Changed files
- docs/backend/{AUTH.md, API.md, DESIGN.md}, docs/INFRA.md
- backend/conftest.py, backend/core/config.py
- backend/modules/auth/{service.py, schemas/__init__.py, schemas/user.py, tests/test_service.py}
- backend/modules/main/{CLAUDE.md, config.py, dependencies.py, rate_limit.py, routers/users.py, tests/test_config.py, tests/test_users.py, tests/test_rate_limit.py}
