# EXEC — 2026-10-25-backend-user-session

## v1
exec_version: 1

### Summary
- P1: `User` model, `id` server default `gen_random_uuid()`, `whatsapp` varchar(16), names varchar(100), `created_at` timestamptz `now()`.
- P2: async Alembic env, version table `alembic_version_auth`, autogenerate limited to the module tables (`include_name`). Revision `0001`.
- P3: `UserCreate` (`extra="forbid"`, WhatsApp normalized then `^\+[1-9]\d{6,14}$`, names trimmed 1-100), `UserRead`.
- P4: `service.create_user` (`INSERT ... RETURNING`), `service.get_user`. Each opens its own session.
- P5: CORS origins from `CORS_ORIGINS` (comma-separated). `GET /api/users/{id}`: Owner check before the id parse; malformed or unknown id -> 404. `GET /api/health`.
- P6: `backend/conftest.py`: `downgrade base` + `upgrade head` once per run (subprocess), `TRUNCATE users` per test. 23 tests.
- P9: `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` also set in the local `frontend/.env` (not committed).
- P10: ruff, pytest 23/23, alembic up/down/check, Frontend lint/typecheck/test/build, Playwright run against uvicorn + PostgreSQL 16: PASS.

### Changed files
- backend/{main.py, conftest.py, .env.example, pyproject.toml, uv.lock} (scaffold added to the repo)
- backend/modules/auth/{service.py, alembic.ini, CLAUDE.md, models/, schemas/, migrations/, tests/test_schemas.py, tests/test_service.py}
- backend/modules/main/{app.py, config.py, dependencies.py, CLAUDE.md, routers/users.py, tests/test_users.py}
- backend/modules/phones/ (scaffold only, unchanged)
- Makefile
- frontend/services/PhoneService.ts, frontend/services/__test__/PhoneService.test.ts, frontend/.env.example
