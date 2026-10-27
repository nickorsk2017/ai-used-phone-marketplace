# CLAUDE.md — modules/auth

Rules for AI coding agents working in `backend/modules/auth/`. Project rules: [../../../CLAUDE.md](../../../CLAUDE.md).

## Sources of truth

- Session token, cookie and access: [docs/backend/AUTH.md](../../../docs/backend/AUTH.md#session-token).
- Allowed calls: [docs/backend/DESIGN.md](../../../docs/backend/DESIGN.md#modules).

## Module boundary

- `services/` is the public interface of the module. `services/__init__.py` re-exports the public functions: `services/token.py` has the session token (standard library only, no database), `services/access.py` has the authentication and the owner check. Other modules import only `services`.
- The module calls only `users.services` and `users.schemas`, never `users.models` or `users.database`.
- No tables, no `models/`, no `database.py` in v1.0.
- No settings and no HTTP: the secret is an argument from `modules/main`, the cookie and the statuses belong to `modules/main`.

## Code

- The token is built and verified with the Python standard library only (`hmac`, `hashlib`, `base64`). The signature is compared with `hmac.compare_digest`.
- Verification never raises: any missing or malformed token returns `None`.
- Functions that read the database take the session of the request as the first argument and never commit: [docs/backend/DESIGN.md](../../../docs/backend/DESIGN.md#database-connection).

## Tests

- `tests/` runs against PostgreSQL from `TEST_DATABASE_*`. Fixtures: `backend/conftest.py`.
