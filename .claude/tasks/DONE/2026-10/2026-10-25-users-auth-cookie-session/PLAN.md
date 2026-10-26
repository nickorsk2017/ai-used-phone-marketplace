# PLAN — 2026-10-25-users-auth-cookie-session

## v1
plan_version: 1

### Steps
- P1 (R1): `git mv backend/modules/auth` -> `backend/modules/users`. Package name `users` in its `pyproject.toml`, `AuthBase` -> `UsersBase`, imports `modules.auth.*` -> `modules.users.*` in models, schemas, service, tests. Workspace members in `backend/pyproject.toml`: `modules/users`, `modules/auth`, `modules/phones`, `modules/main`. `migrations/env.py` collects `UsersBase.metadata`. Revision `0001` untouched.
- P2 (R1, R2): new `backend/modules/auth`: `pyproject.toml` (no third-party dependencies beyond the workspace), `service.py` only, no `models`, `database.py`, `schemas`. Public functions: issue a token for a user ID with a secret; authenticate a token (split, verify the signature in constant time, parse the UUID, load the user through `users.service`), returns `UserRead` or nothing; owner check of two UUIDs. Any malformed token -> nothing, never an exception. `tests/`: unit tests of the token and the owner check, integration test of authenticate against PostgreSQL.
- P3 (R3): `modules/main/config.py`: `session_secret` required, minimum 32 characters; `cookie_secure` default true. Error lines of the configuration check name the variable. `backend/.env.example`: `SESSION_SECRET` placeholder, `COOKIE_SECURE=false` for local HTTP. `app.py`: CORS `allow_credentials=True`.
- P4 (R4, R5): `modules/main/dependencies.py`: cookie constants (name, path, max age 400 days) in one place. `CurrentUser` dependency: reads the `session` cookie, calls `auth.service`, on failure raises 401 with a `Set-Cookie` that removes the cookie, on success sets the cookie again on the response. `owner_access` compares the resource owner with `CurrentUser` through the `auth` owner check. `X-User-Id`, `CurrentUserId` and `OwnedUser` removed.
- P5 (R5): `modules/main/routers/users.py`: `POST /api/users` creates the user through `users.service`, issues the token, sets the cookie, 201 with the user. `GET /me` and `PUT /me` on `CurrentUser`; `/{user_id}` routes removed. Rate limit unchanged (instance renamed `users_rate_limit`).
- P6 (A1, A2): `backend/conftest.py` sets `SESSION_SECRET` and `COOKIE_SECURE=false` for tests (httpx over `http://test` drops `Secure` cookies). `modules/main/tests`: rewrite `test_users.py`, `test_session.py` to the cookie flow; cases of A2; `test_config.py` adds the secret cases; `test_rate_limit.py` imports.
- P7 (R6): Frontend. `utils/apiClient.ts`: `credentials: "include"`, no user header. Remove `utils/session.ts`, `USER_ID_STORAGE_KEY`, `USER_ID_HEADER` from `config/api.ts`. `UserService`: `getCurrent()` and `updateCurrent()` on `/api/users/me`. `AuthService.getCurrentUser`: 401 -> no user. `AuthService.register`: no storage. `stores/sessionStore.ts`: `updateProfile` without the user ID. Tests: `apiClient`, `AuthService`, `UserService`, `HeaderProfile`, `MyListingsPage`, `AddPhoneModal`, `vitest.setup.ts` without `localStorage` session setup.
- P8 (R7): `backend/modules/users/CLAUDE.md`: sources of truth -> `SCHEMAS.md#users-modulesusers`, `AUTH.md#modules`; boundary: called by `main` and `auth`. New `backend/modules/auth/CLAUDE.md`: token and cookie rules -> `AUTH.md#session-token`, no tables, calls only `users.service`, secret as an argument. `backend/modules/main/CLAUDE.md`: cookie and `CurrentUser` instead of `X-User-Id`.
- P9 (A1-A6): `uv sync`, `ruff check`, `make backend-test`, `alembic upgrade head` / `downgrade base` / `check`, `pnpm lint typecheck test build`, browser run against the Backend with local PostgreSQL (A5), grep for `X-User-Id`, `AuthBase`, `modules.auth.models`, `user_id` storage, anchor check of Markdown links (A6).

### Order
P1 -> P2 -> P3 -> P4 -> P5 -> P6 (Backend green) -> P7 -> P8 -> P9.

### Risks
- `Secure` cookie over `http://localhost`: Chrome and Firefox accept it, Safari does not. Local `backend/.env` needs `COOKIE_SECURE=false`.
- Local dev is cross-origin (`:3000` -> `:8000`) but same-site: `SameSite=Lax` cookies are sent with `credentials: "include"`. CORS origin must be exact, no `*`.
- `/api/users/*` rate limit (5 per 10 s) now covers `GET /me` on every page load: `sessionStore.init` already shares one request; browser check A5 watches for 429.
- Re-setting the cookie on 401 removal and on success: both through the response of the dependency; FastAPI keeps `Set-Cookie` of a dependency only when the response is not replaced by an exception handler -> 401 path uses `HTTPException` headers.
- `docs/frontend/STRUCTURE.md` mentions `utils/` generically; no doc names `utils/session.ts`. A remaining mention is a discrepancy for the Validator.

## v2
plan_version: 2
change: Engineer feedback on `COOKIE_SECURE` in `backend/.env.example`. Only P3 and the first risk change, other steps as in v1.

### Steps
- P3 (R3): as v1, except `backend/.env.example`: `COOKIE_SECURE=true` with a comment line above it: Safari and local HTTP builds can reject a `Secure` cookie, set `false` locally if the session is not kept after user creation.

### Risks
- `Secure` cookie over `http://localhost`: Chrome and Firefox accept it, Safari does not. `.env.example` keeps `true`; the comment tells to switch to `false` locally on an authorization error.
