# PLAN — 2026-10-25-frontend-phone-details-id-route

## v1
plan_version: 1

### Steps
- P1 (R1): move the route file to `app/phones/[id]/page.tsx`, delete the `[slug]` folder.
- P2 (R1): `loadPhonePage(id)`: listing or `notFound()`, no redirect.
- P3 (R2): `phoneDetailsPath(id)` in `shared/utils/routes.ts`; update callers (`PhoneCard`, `seo.ts`).
- P4 (R3): delete `utils/slug.ts` and its test.
- P5 (A1): update tests that assert the old URL (search, my-listings, seo, loadPhonePage).
- P6 (A1-A3): lint, typecheck, test, build; `next start` URL checks; grep `slug`.
