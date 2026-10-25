# PLAN — 2026-10-25-frontend-search-page

## v1
plan_version: 1

### Steps
- P1 (R1, R2): scaffold `frontend/` with create-next-app (App Router, TypeScript, Tailwind v4, ESLint, no `src/`). `next.config.ts`: `output: "standalone"`. Remove template assets. Create the STRUCTURE.md folders. Scripts: `typecheck`, `test`.
- P2 (R1, R9): dependencies `@heroui/react`, `@heroui/styles`, `react-hook-form`, `zod`, `@hookform/resolvers`, `zustand`. Dev: `vitest`, `jsdom`, `@vitejs/plugin-react`, Testing Library (`react`, `user-event`, `jest-dom`).
- P3 (R3): `app/globals.css` imports Tailwind, `@heroui/styles` and `themes/theme.css`. `themes/theme.css` holds the HeroUI token overrides (light and dark).
- P4 (R1): `frontend/CLAUDE.md`: Frontend rules as links to docs/frontend/*, no restated facts.
- P5 (R4, R7): `shared/config`: API base URL from `NEXT_PUBLIC_API_BASE_URL` (default same origin), search texts (hint, placeholder, error), condition labels, result limit. `frontend/.env.example`.
- P6 (R8): `types/phone.ts` (`PhoneCondition`, `PhoneOs`, `PhoneListing`), `types/search.ts` (`SearchRequest`, `SearchResponse`).
- P7 (R8): `shared/utils/session.ts` (read `user_id` from `localStorage`, safe on server), `shared/utils/apiClient.ts` (JSON fetch, `X-User-Id` header, typed `ApiError`). `shared/features/search/api.ts`: `searchPhones(prompt)`.
- P8 (R6): `utils/slug.ts` (kebab case), `utils/format.ts` (USD price), `utils/cn.ts`.
- P9 (R9): `stores/searchStore.ts`: `status` (idle | loading | success | error), `results`, `search(prompt)`. Stale responses are ignored.
- P10 (R4, R6, R7, R9): `shared/features/search/`: `schema.ts` (Zod prompt schema), `SearchForm.tsx` (RHF + HeroUI TextField/TextArea/Label/Description/Button; Ctrl/Cmd+Enter submits; submit disabled while empty or loading), `SearchResults.tsx` (loading skeletons, empty state, error Alert, list), `PhoneCard.tsx` (HeroUI Card + Chip, Next `Link` to `/phones/{id}/{slug}`), `SearchPage.tsx` (`"use client"`, composition).
- P11 (R5): `app/page.tsx` server file: `metadata.robots = { index: false, follow: true }`, renders `SearchPage`. `app/layout.tsx`: `lang="en"`, app title.
- P12 (A2): Vitest tests next to the modules.
- P13 (A1, A4): run build, lint, typecheck, tests; grep for hex colors and arbitrary Tailwind values.

### Risks
- `POST /api/search` contract is undefined in docs (TASK constraint): isolated in `types/search.ts` and `shared/features/search/api.ts`.
- Empty-results text is not specified in SEARCH_PAGE.md: placeholder text in `shared/config`, listed as a discrepancy.
- `themes/theme.css` must come from the HeroUI Theme Builder: default tokens until the Engineer exports the theme.
