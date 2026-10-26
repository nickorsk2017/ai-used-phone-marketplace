# PLAN — 2026-10-25-backend-access-rate-limit

## v1
plan_version: 1

### Steps
- P1 (R5): docs first. AUTH.md#access: header only for access checks, Owner rule, statuses, existence of the user checked by endpoints that create a resource. API.md: PUT body and response, 429 on rate limit. INFRA.md#application: per-module limits table (auth 5/10s per IP), in-memory per process, client IP via Uvicorn proxy headers behind Caddy. DESIGN.md#configuration: `.env` path. main/CLAUDE.md: `dependencies.py` and `rate_limit.py` rules, statuses link to AUTH.md.
- P2 (R4): `config.py` of `auth` and `main`: `env_file` = `backend/.env` resolved from `__file__`. `test_config.py` isolates `.env` through the settings config instead of `chdir`.
- P3 (R3): `modules/auth/schemas`: shared user fields base, `UserCreate` and `UserUpdate` on it, extra fields forbidden. `service.update_user` (`UPDATE ... RETURNING`, own session, `None` for an unknown id).
- P4 (R1): `modules/main/dependencies.py`: `CurrentUserId` (401), `owner_access(load, owner_of, path_param)` factory: path id parse (404), load (404), header parse and UUID compare (403), returns the loaded resource. `OwnedUser` for `users`.
- P5 (R2): `modules/main/rate_limit.py`: `RateLimit(limit, window_seconds, clock)` sliding window per client IP, 429 + `Retry-After`, stale keys swept, registry reset for tests. `auth_rate_limit` (5/10s) on the `users` router.
- P6 (R1, R3): `routers/users.py`: GET and PUT on `OwnedUser`, PUT 200 with the updated user.
- P7 (A1-A5): `conftest.py` resets rate limits per test. Tests for P2-P6. ruff, pytest on PostgreSQL 16.

### Risks
- Behind Caddy every request has the Caddy IP unless Uvicorn runs with `--proxy-headers --forwarded-allow-ips`: one shared limit for all users. Deployment files are not in the repo: documented in INFRA.md, Engineer applies on deploy.
- In-memory limit is per process: with N Uvicorn workers the effective limit is N x 5.
- Malformed `X-User-Id` returns 403, not 401: the Frontend resets the session only on 404, the reset comes from the path id check (header and path hold the same stale value).
