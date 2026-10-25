# PLAN — 2026-10-25-frontend-phone-details-page

## v1
plan_version: 1

### Steps
- P1 (R4, R5): `shared/config/api.ts`: stub flag, site URL. `shared/config/phone-details.ts`: page texts, JSON-LD condition map, revalidate period. `.env.example`: new variables; local `.env` with the stub on.
- P2 (R3): `types/phone.ts`: `PhoneContact`.
- P3 (R5): `shared/features/phone-details/schema.ts`: Zod listing schema.
- P4 (R4): `shared/features/phone-details/stub.ts`: fixed stub listings and contacts by UUID; unknown id -> not found. `api.ts`: `getPhone(id)` (server, `null` on 404, schema-validated), `getPhoneContact(id)` (client, `apiClient`); both switch to the stub by the flag.
- P5 (R1): `seo.ts`: `buildPhoneMetadata` (title, 155-char description, canonical, Open Graph `product`), `buildPhoneJsonLd` (`Product` + `Offer`, `<` escaped).
- P6 (R1, R2): `loadPhonePage(id, slug)`: `getPhone` -> `notFound()` | `permanentRedirect` to the canonical path | listing. Request deduplicated with React `cache` between `generateMetadata` and the page.
- P7 (R1, R3): `PhoneDetailsPage.tsx` (Server Component): heading, OS, specs list, price, condition Chip, description, condition note, JSON-LD script, `DealButton`. `DealButton.tsx` (`"use client"`): HeroUI Button + Modal; states loading / contact / error; copy with `navigator.clipboard`, "Copied" state.
- P8 (R1): `app/phones/[id]/[slug]/page.tsx`: `revalidate`, empty `generateStaticParams`, `generateMetadata`, page composition. `app/robots.ts`. `app/layout.tsx`: `metadataBase`.
- P9 (A2): tests next to the modules: schema, seo, loadPhonePage (redirect, 404), DealButton.
- P10 (A1, A3, A4): lint, typecheck, test, build; `next start` with the stub, check HTML, 308, 404, robots; grep hex and arbitrary values.

### Risks
- Contact response shape and server base URL undefined (TASK constraints): isolated in `types/phone.ts` and `api.ts`.
- Clipboard API is unavailable on non-secure origins: error message instead of "Copied".
