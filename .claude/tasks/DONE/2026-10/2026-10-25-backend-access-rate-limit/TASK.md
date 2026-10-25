# TASK — 2026-10-25-backend-access-rate-limit
owner: Engineer
immutable: true

## Requirements
- R1: Access check of `Owner` endpoints as a FastAPI dependency in `modules/main`, reusable by every resource. `X-User-Id` is used only for the access check of the operation: a user reads, updates and deletes only own resources. Ids are compared as UUIDs, not strings. Statuses: missing `X-User-Id` 401, malformed or unknown resource id 404, `X-User-Id` is not the owner 403 (Frontend session reset on 404 keeps working, docs/backend/AUTH.md#session-flow).
- R2: Rate limit on the application level, a separate limit per module, as a FastAPI dependency on the routers of the module. `modules/auth` (`/api/users/*`): 5 requests per 10 seconds per client IP. Exceeded limit: 429 with `Retry-After`.
- R3: `PUT /api/users/{id}` (Owner) per docs/backend/API.md: replaces `whatsapp`, `first_name`, `last_name` with the validation of `POST /api/users`, returns the user. The client cannot change `id` or `created_at`.
- R4: Settings of `modules/auth` and `modules/main` read `backend/.env` by a path resolved from the module file, not from the current directory.
- R5: docs/ updated before the code (CLAUDE.md#1): docs/backend/AUTH.md#access, docs/backend/API.md, docs/INFRA.md#application, docs/backend/DESIGN.md#configuration, backend/modules/main/CLAUDE.md.

## Acceptance
- A1: `ruff check` and `pytest` pass against PostgreSQL.
- A2: Tests: Owner dependency (own 200, no header 401, foreign 403, malformed header 403, malformed path id 404, unknown id 404, UUID in upper case is the same owner) for GET and PUT.
- A3: Tests: PUT updates and returns the user, invalid body 422, `id` or `created_at` in the body 422.
- A4: Tests: 6th request to `/api/users/*` within 10 seconds from one IP is 429 with `Retry-After`; another IP is not limited; the window expires; `/api/health` is not limited.
- A5: Tests: settings read `backend/.env` when the process starts from another directory.

## Constraints
- No new dependencies. Limit storage in process memory; shared storage (Redis): docs/ROADMAP.md#high-load.
- Out of scope: `modules/phones`, `modules/rag`, Frontend changes, deployment files (Caddy, Uvicorn flags are documented only).
