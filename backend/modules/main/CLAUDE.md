# CLAUDE.md — modules/main

Rules for AI coding agents working in `backend/modules/main/`. Project rules: [../../../CLAUDE.md](../../../CLAUDE.md).

## Sources of truth

- Endpoints and access levels: [docs/backend/API.md](../../../docs/backend/API.md).
- `X-User-Id` and the Owner check: [docs/backend/AUTH.md](../../../docs/backend/AUTH.md#access).

## Module boundary

- `main` is the only module that serves HTTP and the only one that calls other modules, through their `service.py`.
- `main` has no tables and no models. Request and response bodies are the Pydantic schemas of the called module.
- `main` owns the session and the transaction of the request: [docs/backend/DESIGN.md](../../../docs/backend/DESIGN.md#database-connection).

## Code

- `app.py`: app factory, CORS, routers under the `/api` prefix. `backend/main.py` only creates the app.
- `routers/<resource>.py`: one router per resource, path relative to `/api`. `routers/health.py`: database check, no rate limit, no request session.
- Every endpoint that calls a service depends on `DbSession` and passes it to the service. `DbSession` uses `scope="function"`: the commit runs before the response is sent.
- `dependencies.py`: access checks, rules and statuses: [docs/backend/AUTH.md](../../../docs/backend/AUTH.md#access). `User` endpoints depend on `CurrentUserId`. `Owner` endpoints depend on a resource dependency built by `owner_access(load, owner_of, path_param)`: it returns the loaded resource, the endpoint does not load it again. No Starlette middleware for access checks: the owner is known only after routing.
- `rate_limit.py`: `RateLimit`, one instance per module, attached to the routers of the module with `dependencies=[Depends(...)]`. Limits: [docs/INFRA.md](../../../docs/INFRA.md#application).

## Tests

- `tests/` calls the app through `httpx.ASGITransport` against PostgreSQL. Fixtures: `backend/conftest.py`.
