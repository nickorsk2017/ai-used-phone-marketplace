# Backend Structure

Module responsibilities: [DESIGN.md](DESIGN.md#modules).

## Folders

```
backend/
  core/
  modules/
    users/
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

- `core`: shared infrastructure of the modules: database settings and connection (see [DESIGN.md](DESIGN.md#database-connection)), `llm.py`: the LangChain client factories (`chat_model`, `embeddings`) and `llm_call`, the structured LLM call with the repeat on an invalid output (see [RAG.md](../ai/RAG.md#errors-and-retries)).
- `modules`: domain modules and `main`, one folder per module: see [Module structure](#module-structure).
- `migrations`: Alembic migrations of all modules, `alembic.ini`: their config. See [SCHEMAS.md](SCHEMAS.md#migrations).
- `main.py`: entry point.
- `conftest.py`: shared test fixtures (PostgreSQL from `TEST_DATABASE_URL`).
- `pyproject.toml`, `uv.lock`: uv workspace of the modules, dev tools (pytest, ruff).
- `.env.example`: template of `backend/.env`. Variables: see [DESIGN.md](DESIGN.md#configuration).

## Module structure

There are two kinds of modules: domain modules and `modules/main`. Module rules: the `CLAUDE.md` of each module.

### Domain module

`modules/users`, `modules/auth`, `modules/phones`, `modules/rag`. A domain module has no HTTP endpoints.

- `models` - SQLAlchemy models, only in a module with tables
- `schemas` - Pydantic schemas for data structure validation, also the request and response bodies of the API
- `services` - public interface of the module. Other modules import only `services` and `schemas`. `services/__init__.py` re-exports the public functions, the files inside are split by dependency: `crud.py` has the database functions (take the session), `ai.py` has the LLM and embedding calls (`modules/phones`, `modules/rag`), `token.py` and `access.py` in `modules/auth`
- other files of the module, for example `prompts.py` in `modules/phones`: internal, imported only inside the module
- `config.py` - settings of the module, only in a module with settings (`modules/phones`, `modules/rag`): see [DESIGN.md](DESIGN.md#configuration)
- `database.py` - declarative Base of the module tables (`UsersBase`), only in a module with tables
- `tests` - unit tests, integration tests
- `pyproject.toml` - file describing dependencies and libraries
- `CLAUDE.md` - rules for AI coding agents: module architecture and code

### `modules/main`

The API for the Frontend. No tables and no models.

- `app.py` - app factory, configuration check, CORS, routers under the `/api` prefix
- `config.py` - settings of the module
- `dependencies.py` - session of the request (`DbSession`), the session cookie and access checks (`CurrentUser`, `owner_access`)
- `rate_limit.py` - rate limits of the modules
- `ai.py` - `AI_ERRORS`: errors of the AI calls of the domain modules left after the retries, mapped to 503
- `routers` - API endpoints, one file per resource (`users.py`, `health.py`, `phones.py`, `my_listings.py`)
- `tests` - unit tests, integration tests
- `pyproject.toml` - file describing dependencies and libraries
- `CLAUDE.md` - rules for AI coding agents: module architecture and code
