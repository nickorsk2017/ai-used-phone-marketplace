# VALIDATION — 2026-10-25-backend-user-session

## v1
validation_version: 1
result: PASS

### Checks
- A1: `ruff check`, `ruff format --check`, `pytest` 23 passed on PostgreSQL 16: PASS.
- A2: PASS (201 + UUID v4 from the database, `id` in body 422, invalid body 422, own user 200, no header 401, foreign header 403, unknown id 404, malformed id 404, CORS preflight).
- A3: `upgrade head`, `downgrade base`, `upgrade head` on an empty database; `alembic check`: no new operations; version table `alembic_version_auth`: PASS.
- A4: `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`: PASS.
- A5: Chromium against uvicorn + PostgreSQL: modal without `user_id` -> `POST /api/users` -> `user_id` in `localStorage`, row in `users`, "Add new phone" and empty list shown -> reload restores the session via `GET /api/users/{id}` -> row deleted -> 404 -> `user_id` removed, modal shown: PASS.
- R1-R6: PASS. Module boundary: `main` imports only `modules.auth.service` and `modules.auth.schemas`.

### Discrepancies (CLAUDE.md#1)
- D1: docs/backend/STRUCTURE.md#module-structure requires `routers` in every module and has no public interface file. docs/backend/API.md: all endpoints are in `modules/main`. Code: `modules/auth` has no routers, `modules/auth/service.py` is the module interface (modules/auth/CLAUDE.md). Fix: add `service.py` to STRUCTURE.md, `routers` for `main` only.
- D2: docs/backend/AUTH.md#access defines no statuses. Code: missing `X-User-Id` 401, foreign resource 403, unknown or malformed id 404 (modules/main/CLAUDE.md). Fix: add the statuses to AUTH.md#access.
- D3: docs/backend/SCHEMAS.md#users-modulesauth defines no WhatsApp format and no lengths. Code: `+<7-15 digits>` after removing separators, `whatsapp` varchar(16), names 1-100 chars. Fix: add to SCHEMAS.md (also D5 of 2026-10-25-frontend-my-listings-page).
- D4: docs/backend/API.md has no request/response bodies of `POST /api/users`, `GET /api/users/{id}` and no `GET /api/health`. Code: body `{whatsapp, first_name, last_name}`, response all `users` fields, health `{"status": "ok"}`. Fix: add to API.md.
- D5: docs/backend/STRUCTURE.md lists only `backend/main.py`. Code also has `backend/conftest.py`, `backend/.env.example`, `modules/<module>/alembic.ini`. Fix: add to STRUCTURE.md.
- D6: docs/INFRA.md#makefile-targets lists `deploy`, `logs`, `migrate`. Code: `backend-install`, `backend-dev`, `backend-test`, `migrate`; local development uses two origins (`:3000` -> `:8000`) with `CORS_ORIGINS`, production is same-origin behind Caddy. Fix: add a local development section to INFRA.md.
