# TASK — 2026-10-25-frontend-header-profile
owner: Engineer
immutable: true

## Requirements
- R1: Avatar and name move from the My listings page header to `AppHeader`, after the navigation links, on every page (docs/features/MY_LISTING.md#edit-profile-flow step 1). The My listings page header keeps only "Add new phone".
- R2: The header loads the session user when `user_id` exists (docs/backend/AUTH.md#session-flow step 1). Concurrent `init` calls share one request.
- R3: Click opens the edit profile modal, `PUT /api/users/{id}` unchanged (2026-10-25-frontend-edit-profile).
- R4: The empty list has no "Add new phone" button, only the text: the page header button is the only one (docs/features/MY_LISTING.md#add-phone-flow step 1).

## Acceptance
- A1: `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build` pass.
- A2: Tests: header shows the user and edits the profile with PUT; header shows nothing without a user; My listings page has no profile button and exactly one "Add new phone" button.

## Constraints
- `ui/` does not import features or stores: the profile block is passed to `AppHeader` from `app/layout.tsx`.
