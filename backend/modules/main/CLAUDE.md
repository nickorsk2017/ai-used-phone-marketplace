# CLAUDE.md — modules/main

Rules for AI coding agents working in `backend/modules/main/`. Project rules: [../../../CLAUDE.md](../../../CLAUDE.md).

## Sources of truth

- Endpoints and access levels: [docs/backend/API.md](../../../docs/backend/API.md).
- Session cookie, `CurrentUser` and the Owner check: [docs/backend/AUTH.md](../../../docs/backend/AUTH.md#cookie), [docs/backend/AUTH.md](../../../docs/backend/AUTH.md#access).

## Module boundary

- `main` is the only module that serves HTTP. It calls the domain modules through their `services/`: [docs/backend/DESIGN.md](../../../docs/backend/DESIGN.md#modules).
- `main` has no tables and no models. Request and response bodies are the Pydantic schemas of the called module.
- `main` owns the session and the transaction of the request: [docs/backend/DESIGN.md](../../../docs/backend/DESIGN.md#database-connection).

## Code

- `app.py`: app factory, CORS with credentials for `CORS_ORIGINS`, routers under the `/api` prefix. `backend/main.py` only creates the app.
- `routers/<resource>.py`: one router per resource, path relative to `/api`. `routers/health.py`: database check, no rate limit, no request session.
- Every endpoint that calls a service depends on `DbSession` and passes it to the service. `DbSession` uses `scope="function"`: the commit runs before the response is sent.
- Exception: `POST /api/phones` writes through `run_in_transaction` from `core/database.py`, not through `DbSession`: [docs/backend/DESIGN.md](../../../docs/backend/DESIGN.md#transaction-retry). Guardrail 1 and the embedding run before it and are not repeated by the retry. Endpoints with LLM or embedding calls depend on `CurrentUserShortSession`, not `CurrentUser`: authentication does not keep a connection open during the slow calls.
- `ai.py`: `AI_ERRORS`, the errors left after the retries of the AI calls of `modules/phones` and `modules/rag`, map to 503. `main` creates no AI clients: each domain module creates its own from its settings.
- `dependencies.py`: the session cookie and access checks, rules and statuses: [docs/backend/AUTH.md](../../../docs/backend/AUTH.md#access). Cookie name, path, max age and flags are defined there only; `set_session_cookie` is the only place that sets the cookie. `User` endpoints depend on `CurrentUser`: it authenticates through `auth.services`, sets the cookie again, and on 401 removes it. `Owner` endpoints depend on a resource dependency built by `owner_access(load, owner_of, path_param)`: it returns the loaded resource, the endpoint does not load it again. No Starlette middleware for access checks: the owner is known only after routing.
- `rate_limit.py`: `RateLimit`, one instance per module, attached to the routers of the module with `dependencies=[Depends(...)]`. Limits: [docs/INFRA.md](../../../docs/INFRA.md#application).

## Tests

- `tests/` calls the app through `httpx.ASGITransport` against PostgreSQL. Fixtures: `backend/conftest.py`.
