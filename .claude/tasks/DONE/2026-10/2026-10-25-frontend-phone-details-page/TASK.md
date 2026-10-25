# TASK — 2026-10-25-frontend-phone-details-page
owner: Engineer
immutable: true

## Requirements
- R1: Page `/phones/[id]/[slug]` per docs/features/PHONE_DETAILS.md: route, page content (items 1-7), rendering (Server Component, `revalidate = 60`, empty `generateStaticParams`), SEO (metadata, JSON-LD `Product`/`Offer`, `app/robots.ts`), errors (404, 500). Route file only composes components from `shared/features` (docs/frontend/STRUCTURE.md).
- R2: Wrong `slug` returns a 308 redirect to `/phones/{id}/{slug}` with the current model slug.
- R3: Deal flow per docs/features/PHONE_DETAILS.md#deal-flow: "Deal" button and modal are the only Client Components; `GET /api/phones/{id}/contact` on click; modal shows the WhatsApp number and a "Copy WhatsApp number" button (Clipboard API, "Copied" confirmation). The number is not in the server HTML and not in JSON-LD.
- R4: Stub data source (Backend is not implemented yet). `GET /api/phones/{id}` and `GET /api/phones/{id}/contact` return stub data when `NEXT_PUBLIC_API_STUB=true`; otherwise the real Backend is called. The stub is isolated in one module and is removed without changes to the page components.
- R5: API response of `GET /api/phones/{id}` validated with a Zod schema in the shape of `types/phone.ts`. UI rules of docs/frontend/DESIGN.md#ui, texts in `shared/config/`.

## Acceptance
- A1: `npm run lint`, `npm run typecheck`, `npm test`, `npm run build` pass after a clean `npm ci`.
- A2: Unit tests: listing schema, slug redirect, 404, JSON-LD (condition mapping, no WhatsApp), metadata, Deal modal (load contact, copy, "Copied", load error).
- A3: Production server with the stub: server HTML of a stub listing contains model name, parameters, price, condition, description, condition note, JSON-LD; does not contain the WhatsApp number. Wrong slug -> 308. Unknown id -> 404. `/robots.txt` allows `/phones/`, disallows `/my-listings` and `/api/`.
- A4: No hex colors, no arbitrary Tailwind values, English only. Search and My listings tests still pass.

## Constraints
- Not defined in docs, assumptions listed as discrepancies:
  - `GET /api/phones/{id}/contact` -> `{whatsapp, first_name, last_name}` (docs/backend/API.md), 404 when the listing does not exist.
  - Server-side base URL of the Backend and the site URL for `metadataBase` (canonical, `og:url`) are not in docs/INFRA.md: `NEXT_PUBLIC_API_BASE_URL` and `NEXT_PUBLIC_SITE_URL`.
  - Stub flag `NEXT_PUBLIC_API_STUB` is a temporary development switch, not described in docs.
- Lighthouse and Rich Results Test (PHONE_DETAILS.md acceptance 3, 6) need a public URL: out of scope, checked by the Engineer after deployment.
