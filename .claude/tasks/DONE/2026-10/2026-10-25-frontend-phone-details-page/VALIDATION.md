# VALIDATION — 2026-10-25-frontend-phone-details-page

## v1
validation_version: 1
result: PASS

### Checks
- R1: route, content 1-7, `revalidate = 60`, empty `generateStaticParams`, metadata, JSON-LD, robots, 404: OK (docs/features/PHONE_DETAILS.md).
- R2: wrong slug -> 308 to the canonical URL: OK.
- R3: Deal button and modal are the only page Client Components; contact loaded on click; copy + "Copied"; number absent from server HTML and JSON-LD: OK.
- R4: stub isolated in `stub.ts`, switched in `api.ts` only: OK.
- R5: Zod schema, texts in `shared/config/phone-details.ts`, HeroUI tokens: OK.
- A1: clean `npm ci` + lint, typecheck, 65/65 tests, build: OK. A2: OK. A3: OK (EXEC P10). A4: no hex, no arbitrary values, English only: OK.

### Issues
- none

### Discrepancies for the Engineer (CLAUDE.md#1)
- D1: docs/backend/API.md lists the fields of `GET /api/phones/{id}/contact` but not the response shape or the 404 case. Implemented `{whatsapp, first_name, last_name}`, 404 -> error in the modal. Suggested: add the response body to API.md.
- D2: docs/INFRA.md has no server-side Backend URL for Server Components and no public site URL for `metadataBase`. Implemented `NEXT_PUBLIC_API_BASE_URL` (relative URLs fail on the server) and `NEXT_PUBLIC_SITE_URL`. Suggested: add both variables to INFRA.md.
- D3: PHONE_DETAILS.md#metadata requires `og:type = product`; the Next.js Metadata API has no `product` type. Implemented as a `<meta property>` hoisted into `<head>`. Suggested: note it in PHONE_DETAILS.md.
- D4: docs/frontend/DESIGN.md#ui requires HeroUI components; PHONE_DETAILS.md#rendering allows only the Deal button and modal as Client Components, and HeroUI `Chip` is a Client Component. Implemented `ConditionBadge` with HeroUI `chipVariants`. Suggested: allow HeroUI style functions for server markup in DESIGN.md.
- D5: `NEXT_PUBLIC_API_STUB` is not in the docs. Temporary until the Backend endpoints exist; remove `stub.ts` and the flag then.
- D6: page headings and modal texts are not in PHONE_DETAILS.md; the modal shows the seller name (returned by the contact endpoint, promised in the My listings profile text). Suggested: add the texts to PHONE_DETAILS.md#deal-flow.
- D7: FastAPI returns 422 for a non-UUID `id`; PHONE_DETAILS.md#errors names 404 only. Implemented 422 -> 404 page. Suggested: state it in PHONE_DETAILS.md#errors.
