# EXEC — 2026-10-25-frontend-phone-details-id-route

## v1
exec_version: 1

### Summary
- P1-P4: route `app/phones/[id]/page.tsx`; `[slug]` folder, `utils/slug.ts`, `utils/slug.test.ts` deleted; `loadPhonePage(id)` without redirect; `phoneDetailsPath(id)`.
- P5: URL assertions updated in search, my-listings, seo, loadPhonePage tests.
- P6: clean `npm ci`: lint, typecheck, 63/63 tests, build pass. `next start`: `/phones/{id}` 200, canonical, `og:url`, `Offer.url` = `/phones/{id}`; unknown id 404; old `/phones/{id}/{slug}` 404. No `slug` in `frontend/` and `docs/`.

### Changed files
- frontend/app/phones/[id]/page.tsx (moved from `[id]/[slug]/page.tsx`)
- frontend/shared/utils/routes.ts
- frontend/shared/ui/PhoneCard.tsx
- frontend/shared/features/phone-details/{loadPhonePage.ts, loadPhonePage.test.ts, seo.ts, seo.test.ts}
- frontend/shared/features/search/SearchPage.test.tsx
- frontend/shared/features/my-listings/MyListingsPage.test.tsx
- frontend/utils/{slug.ts, slug.test.ts} (deleted)
