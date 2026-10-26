# PLAN — 2026-10-25-backend-user-session

## v1
plan_version: 1

### Steps
- P1 (R1): `modules/auth/models`: `User` on `AuthBase`. `id` UUID PK with server default `gen_random_uuid()`, `whatsapp`, `first_name`, `last_name` NOT NULL, `created_at` timestamptz server default `now()`.
- P2 (R1, A3): `modules/auth/migrations` (async Alembic env, `alembic.ini` in the module), version table `alembic_version_auth`, revision `0001` creates `users`.
- P3 (R2): `modules/auth/schemas`: `UserCreate` (extra fields forbidden; names trimmed, 1-100 chars; WhatsApp normalized like the Frontend: separators removed, `+<7-15 digits>`), `UserRead` (all fields).
- P4 (R2, R3, R4): `modules/auth/service.py`: public interface of the module, `create_user`, `get_user`. Opens its own session: `main` never touches the auth database.
- P5 (R4): `modules/main/config.py` (CORS origins, default `http://localhost:3000`), `modules/main/dependencies.py` (`X-User-Id` -> 401 when missing, Owner check -> 403 on mismatch), `modules/main/routers/users.py` (`POST /api/users` 201, `GET /api/users/{id}`: malformed or unknown id -> 404), `modules/main/app.py` (app factory, CORS, routers under `/api`, `GET /api/health`). `backend/main.py` exposes `app`.
- P6 (A1, A2): `backend/conftest.py`: test database from `TEST_DATABASE_URL`, `alembic upgrade head` once, `users` truncated per test, ASGI client. Tests in `modules/auth/tests` (schemas, service) and `modules/main/tests` (endpoints, A2 cases).
- P7 (R1, R4): `CLAUDE.md` in `modules/auth` and `modules/main` (docs/backend/STRUCTURE.md#module-structure). `backend/.env.example`.
- P8 (R6): Makefile: `backend-install`, `backend-dev`, `backend-test`, `migrate`.
- P9 (R5): `frontend/services/PhoneService.ts`: `getMyListings` returns an empty list when `API_STUB_ENABLED`. `frontend/.env.example`: `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`.
- P10 (A1-A5): ruff, pytest, migrations up/down, Frontend checks, browser run against the Backend and a local PostgreSQL.

### Risks
- Supabase transaction pooler: prepared statements disabled (already in `database.py`). Migrations should use the session pooler or the direct URL.
- 401/403 statuses and the WhatsApp format are not in docs/: listed as discrepancies by the Validator.
