# TASK — 2026-10-25-frontend-edit-profile
owner: Engineer
immutable: true

## Requirements
- R1: My listings header: user avatar (initials) and full name next to "Add new phone", per docs/features/MY_LISTING.md#edit-profile-flow step 1.
- R2: Click opens the user modal used for the user creation, in edit mode with the current values (steps 2-3).
- R3: Save calls `PUT /api/users/{id}` (docs/backend/API.md) and updates the session user; error handling per step 5.

## Acceptance
- A1: `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build` pass.
- A2: Tests: `UserService.update` sends PUT with the body; My listings edits the WhatsApp number, the PUT body is correct and the header shows the updated name.

## Constraints
- Frontend only. `PUT /api/users/{id}` already exists in the Backend.
- No new dependencies. Files at most 200 lines.
