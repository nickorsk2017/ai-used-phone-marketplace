# TASK — 2026-10-26-phone-details-api
owner: Engineer
immutable: true

## Requirements
- R1: `GET /api/phones/{id}`, Public: listing details without `user_id` (docs/backend/API.md, docs/features/PHONE_DETAILS.md#rendering).
- R2: `GET /api/phones/{id}/contact`, Public: `whatsapp`, `first_name`, `last_name` of the listing owner (docs/features/PHONE_DETAILS.md#deal-flow, docs/backend/AUTH.md#access).
- R3: Malformed or unknown listing id: 404. Listing whose owner does not exist: contact 404.

## Acceptance
- A1: Response of R1 matches `frontend/schemas/phoneSchemas.ts` `phoneSchema`, no `user_id`.
- A2: Response of R2 matches `phoneContactSchema`, contains no ids.
- A3: Integration tests for R1-R3 in `backend/modules/main/tests/`, all backend tests pass.
- A4: Frontend `/phones/[id]` works against the Backend without changes to the Frontend.

## Constraints
- Module boundary: `main` calls `phones` and `users` through `services/` only (backend/modules/main/CLAUDE.md).
- No rate limit on these endpoints in v1.0 (docs/INFRA.md#application lists the contact limit as planned).
