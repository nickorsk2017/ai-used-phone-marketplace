# TASK — 2026-10-25-frontend-my-listings-page
owner: Engineer
immutable: true

## Requirements
- R1: Page `/my-listings` per docs/features/MY_LISTING.md: Client Component, `noindex` (docs/frontend/DESIGN.md#pages). Route file only composes a component from `shared/features`.
- R2: Session flow per docs/backend/AUTH.md#session-flow: read `user_id` from `localStorage`; missing -> user creation modal (fields of docs/backend/SCHEMAS.md#users-modulesauth) -> `POST /api/users` -> save `id`; present -> `GET /api/users/{id}`; 404 -> remove `user_id`, show the modal.
- R3: List of the user's listings from `GET /api/my-listings`.
- R4: "Add new phone" modal per docs/features/MY_LISTING.md#add-phone-flow steps 1-7 and #description-response: model name -> `POST /api/phones/description`; editable description, camera, battery, display; read-only model name and OS; hidden model code; condition note; condition select; price in USD (positive integer). HTTP 422 -> `Model not found. Check that the model really exists.` next to the model name field.
- R5: Frontend Regex layer of Guardrail 1 (docs/ai/GUARDRAILS.md#guardrail-1-phone-saving): block credit card numbers, phone numbers and links in the listing text before `POST /api/phones`.
- R6: Save via `POST /api/phones`. On error the form keeps the data and the user can retry (MY_LISTING.md#add-phone-flow step 10).
- R7: Delete a listing via `DELETE /api/phones/{id}` with a confirmation.
- R8: Forms with React Hook Form + Zod, state in Zustand stores, UI rules of docs/frontend/DESIGN.md#ui.
- R9: App header with navigation between Search (`/`) and My listings (`/my-listings`).

## Acceptance
- A1: `npm run lint`, `npm run typecheck`, `npm test`, `npm run build` pass after a clean `npm ci`.
- A2: Unit tests: user schema, listing schema, guardrail regex, session flow (no user, existing user, 404), add phone flow (generate, 422, guardrail block, save, save error), delete.
- A3: Server HTML of `/my-listings` contains `<meta name="robots" content="noindex...">`.
- A4: No hex colors, no arbitrary Tailwind values, English only.
- A5: Search page tests still pass.

## Constraints
- Request and response bodies of `/api/users`, `/api/my-listings`, `/api/phones/description`, `/api/phones` are not defined in docs/backend/API.md. Assumptions, listed as discrepancies:
  - `POST /api/users` `{whatsapp, first_name, last_name}` -> `User`; `GET /api/users/{id}` -> `User`.
  - `GET /api/my-listings` -> `{listings: PhoneListing[]}`.
  - `POST /api/phones/description` `{model_name}` -> description response of MY_LISTING.md.
  - `POST /api/phones` listing fields without `id`, `user_id`, timestamps -> `PhoneListing`. `DELETE /api/phones/{id}` -> 204.
- Scope: create and delete. Listing edit (`PATCH`) and user profile edit (`PUT`) are out of scope: no UI is specified.
