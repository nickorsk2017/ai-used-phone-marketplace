# VALIDATION — 2026-10-25-backend-access-rate-limit

## v1
validation_version: 1
result: PASS

### Checks
- A1: `ruff check`, `ruff format --check`, `pytest` 42 passed on PostgreSQL 16, `alembic check` no new operations: PASS.
- A2: own 200, no header 401, foreign 403, malformed header 403, malformed path id 404, unknown id 404, upper case UUID 200; GET and PUT: PASS.
- A3: PUT 200 and persisted, blank name 422, `id` 422, `created_at` 422: PASS.
- A4: 6th request 429 with `Retry-After` 1-10, other IP not limited, `/api/health` not limited, window expiry and sweep with a fake clock: PASS.
- A5: both `ENV_FILE` equal `backend/.env`; settings read an absolute `env_file` from another directory: PASS.
- R1-R5: PASS. Frontend session reset: stale `user_id` in header and path -> 404 (test `test_get_malformed_user_id_returns_404`).

### Discrepancies (CLAUDE.md#1)
- D1: TASK.md R4 names `modules/auth` settings. Code: database settings are in `core/config.py` (parallel refactor, docs/backend/DESIGN.md#database-connection). Fix: none in code, R4 applied to `core/config.py`.
- D2: docs/backend/STRUCTURE.md#module-structure lists `routers` and `config.py` in every module and no `service.py`. Code: `modules/auth` has `service.py`, no routers and no `config.py`; `modules/main` has `dependencies.py` and `rate_limit.py`. Fix: describe the domain module and `main` separately (D1 of 2026-10-25-backend-user-session is still open).
- D3: docs/INFRA.md#application requires Uvicorn `--proxy-headers --forwarded-allow-ips` and Caddy trusted proxies. Deployment files are not in the repository: cannot be validated. Fix: apply in the Docker Compose and Caddy config on deploy.
- D4: docs/backend/AUTH.md#access: an endpoint that creates a resource checks that the user exists. No such endpoint yet (`modules/phones` out of scope). Fix: acceptance item for `POST /api/phones`.
