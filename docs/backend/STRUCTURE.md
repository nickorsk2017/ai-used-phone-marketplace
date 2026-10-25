# Backend Structure

Module responsibilities: [DESIGN.md](DESIGN.md#modules).

## Folders

```
backend/
  core/
  modules/
    auth/
    phones/
    rag/
    main/
  migrations/
  alembic.ini
  main.py
  conftest.py
  pyproject.toml
  uv.lock
  .env.example
```

- `core`: shared infrastructure of the modules: database settings and connection. See [DESIGN.md](DESIGN.md#database-connection).
- `modules`: domain modules and `main`, one folder per module: see [Module structure](#module-structure).
- `migrations`: Alembic migrations of all modules, `alembic.ini`: their config. See [SCHEMAS.md](SCHEMAS.md#migrations).
- `main.py`: entry point.
- `conftest.py`: shared test fixtures (PostgreSQL from `TEST_DATABASE_URL`).
- `pyproject.toml`, `uv.lock`: uv workspace of the modules, dev tools (pytest, ruff).
- `.env.example`: template of `backend/.env`. Variables: see [DESIGN.md](DESIGN.md#configuration).

## Module structure

There are two kinds of modules: domain modules and `modules/main`. Module rules: the `CLAUDE.md` of each module.

### Domain module

`modules/auth`, `modules/phones`, `modules/rag`. A domain module has no HTTP endpoints and no settings of its own.

- `models` - SQLAlchemy models
- `schemas` - Pydantic schemas for data structure validation, also the request and response bodies of the API
- `service.py` - public interface of the module. Other modules import only `service.py` and `schemas`
- `database.py` - declarative Base of the module tables (`AuthBase`)
- `tests` - unit tests, integration tests
- `pyproject.toml` - file describing dependencies and libraries
- `CLAUDE.md` - rules for AI coding agents: module architecture and code

### `modules/main`

The API for the Frontend. No tables and no models.

- `app.py` - app factory, configuration check, CORS, routers under the `/api` prefix
- `config.py` - settings of the module
- `dependencies.py` - session of the request (`DbSession`) and access checks (`CurrentUserId`, `owner_access`)
- `rate_limit.py` - rate limits of the modules
- `routers` - API endpoints, one file per resource (`users.py`, `health.py`)
- `tests` - unit tests, integration tests
- `pyproject.toml` - file describing dependencies and libraries
- `CLAUDE.md` - rules for AI coding agents: module architecture and code
