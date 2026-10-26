# EXEC — 2026-10-25-users-auth-cookie-session

## v1
exec_version: 1

### Summary
- P1: `modules/auth` -> `modules/users` (`UsersBase`, package `users`), imports, workspace members, `migrations/env.py`. Revision `0001` unchanged.
- P2: `modules/auth/service.py`: `issue_token`, `verify_token` (never raises), `authenticate` (signature + `users.service.get_user`), `is_owner`. Standard library only, `hmac.compare_digest`.
- P3: `MainSettings.session_secret` (required, min 32), `cookie_secure` (default true); config errors print the variable name upper-case like `core`. CORS `allow_credentials=True`. `.env.example`: `SESSION_SECRET=` empty (the configuration check forces a value), `COOKIE_SECURE=true` with the Safari comment of PLAN v2.
- P4: `dependencies.py`: cookie constants, `set_session_cookie`, `CurrentUser` (sets the cookie again; 401 via `HTTPException` headers removes it), `owner_access` on `CurrentUser` + `auth.is_owner`. `CurrentUserId`, `OwnedUser`, `X-User-Id` removed.
- P5: `routers/users.py`: `POST /api/users` sets the cookie, `GET /me`, `PUT /me`; `/{user_id}` removed. `auth_rate_limit` -> `users_rate_limit`.
- P6: `conftest.py` sets `SESSION_SECRET` and `COOKIE_SECURE=false`. New `main/tests/test_access.py` (Owner level through a probe route, it lost its only endpoint). 72 tests.
- P7: `apiClient` `credentials: "include"`, `utils/session.ts` and the storage/header constants removed, `UserService.getCurrent/updateCurrent`, `AuthService` 401 -> no user, `sessionStore.updateProfile` 401 -> `anonymous`. 83 tests.
- P8: `modules/users/CLAUDE.md`, new `modules/auth/CLAUDE.md`, `modules/main/CLAUDE.md` cookie and `CurrentUser`.
- P9: run in a Linux container with PostgreSQL 16: ruff, pytest 72/72, alembic upgrade/check/downgrade/upgrade, pnpm lint/typecheck/test 83/83/build, Playwright Chromium against uvicorn (`COOKIE_SECURE=true`) + `next start`: A5 PASS. Anchors: 0 broken.

### Notes for the Validator
- A5 first run: the 6th `/api/users/*` request within 10 s returned 429 (create, reload, edit, reload, reload). The rerun with an 11 s pause passed. Limit is defined in docs/INFRA.md#application, not changed.
- A6: `X-User-Id` remains only in 3 tests that assert it is not sent or not accepted (`main/tests/test_users.py`, `apiClient.test.ts`, `MyListingsPage.test.tsx`).
- `backend/uv.lock` regenerated with uv 0.13.4 (`revision = 5`).
- Old files moved, not deleted (folder has no delete permission): `_temp/old-modules-auth/`, `_temp/old-session.ts`. `_temp/` is gitignored.

### Changed files
- backend/{.env.example, conftest.py, pyproject.toml, uv.lock, migrations/env.py}
- backend/modules/users/ (moved from modules/auth: CLAUDE.md, pyproject.toml, database.py, service.py, models/, schemas/, tests/)
- backend/modules/auth/{__init__.py, pyproject.toml, service.py, CLAUDE.md, tests/__init__.py, tests/test_service.py} (new)
- backend/modules/main/{CLAUDE.md, app.py, config.py, dependencies.py, rate_limit.py, routers/users.py}
- backend/modules/main/tests/{test_access.py (new), test_config.py, test_rate_limit.py, test_session.py, test_users.py}
- frontend/{config/api.ts, utils/apiClient.ts, services/AuthService.ts, services/UserService.ts, stores/sessionStore.ts, vitest.setup.ts}
- frontend/utils/session.ts (removed)
- frontend tests: utils/__test__/apiClient.test.ts, services/__test__/{AuthService,UserService}.test.ts, features/__test__/profile/HeaderProfile.test.tsx, features/__test__/my-listings/{MyListingsPage,AddPhoneModal}.test.tsx
