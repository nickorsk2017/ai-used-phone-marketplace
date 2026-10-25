# TASK — 2026-10-25-frontend-phone-details-id-route
owner: Engineer
immutable: true

## Requirements
- R1: Phone details route is `/phones/[id]` per docs/features/PHONE_DETAILS.md#route (updated: no `slug`). The `/phones/[id]/[slug]` route and the slug redirect are removed.
- R2: All links to the page (Search results, My listings), canonical, `og:url` and JSON-LD `Offer.url` use `/phones/{id}`.
- R3: Code that only served the slug (`utils/slug.ts`) is removed.

## Acceptance
- A1: `npm run lint`, `npm run typecheck`, `npm test`, `npm run build` pass after a clean `npm ci`.
- A2: Production server with the stub: `/phones/{id}` returns 200 with canonical `/phones/{id}`; unknown id returns 404; `/phones/{id}/anything` returns 404.
- A3: No `slug` left in `frontend/` source and `docs/`.

## Constraints
- docs/features/PHONE_DETAILS.md and docs/frontend/DESIGN.md#pages already updated by the Engineer.
