# VALIDATION — 2026-10-25-users-auth-cookie-session

## v1
validation_version: 1
result: PASS

### Checks
- A1: `ruff check`, `ruff format --check`, `pytest` 72 passed on PostgreSQL 16, with the `backend/uv.lock` of the repository (`uv sync --locked --all-packages`): PASS.
- A2: token issue/verify, other secret, replaced user ID, malformed tokens, unknown user 401 + cookie removed, missing cookie 401, tampered cookie 401, attributes (`HttpOnly`, `SameSite=Lax`, `Path=/api`, `Max-Age` 34560000, `Secure` per `COOKIE_SECURE`), cookie set again on `GET /me`, `GET`/`PUT /me`, `/{id}` routes 404, rate limit on `/api/users/me`, missing and short `SESSION_SECRET`, Owner level 200/403/404/401, CORS credentials: PASS.
- A3: `upgrade head`, `check` (no new operations), `downgrade base`, `upgrade head`: PASS.
- A4: `pnpm lint`, `pnpm typecheck`, `pnpm test` 83 passed, `pnpm build`: PASS.
- A5: Chromium with `COOKIE_SECURE=true` against uvicorn + `next start`: cookie `HttpOnly`, `Secure`, `Lax`, `/api`, 400 days; `document.cookie` on `/api` empty; no `localStorage` key; reload restores; profile edit saved in `users`; deleted row -> modal, cookie removed: PASS (see D1).
- A6: no `AuthBase`, `modules.auth.models`, `USER_ID_STORAGE_KEY`; `X-User-Id` only in 3 negative tests (not sent, not accepted); 0 broken anchors in `docs/`, `README.md`, `backend/modules/*/CLAUDE.md`: PASS.
- R1-R7: PASS. Calls: `main` -> `users.service`, `auth.service`; `auth` -> `users.service`, `users.schemas`; no other cross-module imports. Server-side `fetch` with `credentials: "include"` (Phone details SSG) accepted by Node fetch.

### Discrepancies (CLAUDE.md#1), non-blocking
- D1: docs/INFRA.md#application: `/api/users/*` 5 requests per 10 s per IP. docs/backend/AUTH.md#session-flow: `GET /api/users/me` on every page. A5 first run: create, reload, edit, reload, reload -> the 6th request returned 429 and the session state became `error`. Fix (Engineer): a separate higher limit for `GET /api/users/me`, or the limit only on `POST /api/users` and `PUT /api/users/me`.
- D2: docs/backend/AUTH.md#cookie: the cookie is set again "on every response of a request with a valid session". Code: only on `User` and `Owner` endpoints, Public endpoints do not read the cookie. Fix: AUTH.md "on every response of a `User` or `Owner` endpoint".
- D3: docs/backend/STRUCTURE.md#domain-module lists `schemas` for every domain module. Code: `modules/auth` has only `service.py` (allowed by AUTH.md#modules). Fix: `schemas` "when the module exposes data structures".
- D4: README.md#getting-started names only the Supabase connection and the OpenAI key for `.env`. Code: `SESSION_SECRET` is required, the API does not start without it. Fix: add `SESSION_SECRET` (at least 32 characters) and `COOKIE_SECURE` to the step, link DESIGN.md#configuration.

### Notes
- `PUT /api/users/me` returns 401 without removing the cookie when the user disappears inside the request. Not reachable in v1.0 (no user deletion endpoint).
