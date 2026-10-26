# TASK — 2026-10-25-users-auth-cookie-session
owner: Engineer
immutable: true

## Requirements
- R1: Split `modules/auth` into `modules/users` and `modules/auth` per docs/backend/DESIGN.md#modules and docs/backend/AUTH.md#modules. `modules/users`: `users` table on `UsersBase`, models, schemas, CRUD in `service.py` (moved from the current `modules/auth`). `modules/auth`: session token, authentication of a request, owner check, no tables. `modules/auth` calls only `users.service`.
- R2: Session token per AUTH.md#session-token: `<user_id>.<signature>`, HMAC-SHA256 with `SESSION_SECRET`, constant-time comparison, no expiration. The secret is passed by `modules/main`.
- R3: `modules/main`: settings `SESSION_SECRET` and `COOKIE_SECURE` per DESIGN.md#configuration, included in the configuration check. `backend/.env.example` updated. CORS allows credentials for `CORS_ORIGINS`.
- R4: Cookie per AUTH.md#cookie: set by `POST /api/users`, set again on every response of a request with a valid session, removed on 401. `X-User-Id` is removed from the Backend.
- R5: Endpoints per docs/backend/API.md: `POST /api/users`, `GET /api/users/me`, `PUT /api/users/me`. `GET /api/users/{id}` and `PUT /api/users/{id}` are removed. Access levels and statuses per AUTH.md#access: `CurrentUser` dependency, `owner_access` uses the current user.
- R6: Frontend per AUTH.md#session-flow and docs/frontend/SCHEMAS.md: every API request with `credentials: "include"`, session loaded by `GET /api/users/me`, 401 shows the user creation modal, profile saved by `PUT /api/users/me`. No `user_id` in `localStorage`, no `X-User-Id` header.
- R7: Module rules: `backend/modules/users/CLAUDE.md` (moved from `modules/auth`, links fixed) and a new `backend/modules/auth/CLAUDE.md`. `backend/modules/main/CLAUDE.md` describes the cookie and `CurrentUser` instead of `X-User-Id`.

## Acceptance
- A1: `make backend-test` passes against PostgreSQL. `ruff check` passes.
- A2: Backend tests: token issue and verify, tampered signature, unknown user (401, cookie removed), missing cookie (401), cookie attributes (`HttpOnly`, `SameSite=Lax`, `Path=/api`, `Max-Age` 400 days, `Secure` from `COOKIE_SECURE`), cookie set again on a valid request, `GET` and `PUT /api/users/me`, rate limit of `/api/users/*`, configuration error without `SESSION_SECRET` or with a secret shorter than 32 characters.
- A3: `alembic upgrade head` and `downgrade base` work on an empty database. `alembic check` reports no new operations: the `users` table is unchanged.
- A4: Frontend `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build` pass.
- A5: Browser check against the running Backend: user creation sets the `session` cookie, `document.cookie` does not contain it, `localStorage` has no `user_id`, a reload restores the session, the profile edit saves, a deleted user in the database brings back the user creation modal.
- A6: No references to `X-User-Id`, `AuthBase` or `modules.auth.models` remain in `backend/` and `frontend/`. All Markdown anchor links in `docs/` and `backend/modules/*/CLAUDE.md` resolve.

## Constraints
- docs/ is already updated and is the source of truth for this task. A discrepancy found during the task is reported, not resolved in code.
- No new migration: the `users` table and its revision `0001_create_users.py` stay as they are.
- No new dependencies for the token: Python standard library only.
- Out of scope: logout, token expiration, a `sessions` table, `modules/phones`, `modules/rag`.
