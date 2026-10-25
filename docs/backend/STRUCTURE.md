# Backend Structure

Module responsibilities: [DESIGN.md](DESIGN.md#modules).

## Folders

```
backend/
  modules/
    auth/
    phones/
    rag/
    main/
  main.py
```

- `modules`: domain modules, one folder per module.
- `main.py`: entry point.

## Module structure

Each module in `modules/` contains:

- `models` - contains SQLAlchemy models
- `routers` - describes API endpoints
- `schemas` - Pydantic schemas for data structure validation
- `migrations` - Alembic migrations for the PostgreSQL DB
- `tests` - unit tests, integration tests
- `config.py` - module config file
- `pyproject.toml` - file describing dependencies and libraries
- `CLAUDE.md` - rules for AI coding agents: module architecture and code
