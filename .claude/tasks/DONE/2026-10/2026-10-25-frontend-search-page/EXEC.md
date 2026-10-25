# EXEC — 2026-10-25-frontend-search-page

## v2
exec_version: 2

### Summary
- V1-1: fetch mock typed as `vi.fn<typeof fetch>`, request body read with optional chaining.

### Changed files
- frontend/shared/features/search/SearchPage.test.tsx

## v1
exec_version: 1

### Summary
- P1: create-next-app 16.4.3 (App Router, TS, Tailwind v4, ESLint). `cacheComponents`/`partialPrefetching` of the template removed: they disable the `revalidate` segment config required by docs/features/PHONE_DETAILS.md#rendering. `output: "standalone"`. Scripts `typecheck` (`next typegen && tsc --noEmit`), `test` (Vitest).
- P2: `@heroui/react@3.2.6`, `@heroui/styles@3.2.6`, `react-hook-form`, `zod@4`, `@hookform/resolvers@5` (v6 has an unresolvable peer), `zustand@5`. `@types/node@22` (Vitest peer).
- P3: Google font removed: `next/font/google` fails the build without network access (Docker/CI). HeroUI font stack.
- P5: texts in `shared/config/search.ts`; base URL `NEXT_PUBLIC_API_BASE_URL`, default same origin.
- P9: store keeps the last `prompt`, so the field is restored after Back navigation; an older response is ignored when a new search starts (AbortController).
- P10: submit by button or Ctrl/Cmd+Enter; whole card is a link (stretched link).
- P12: 12 tests, 4 files.

### Changed files
- frontend/{package.json, package-lock.json, next.config.ts, tsconfig.json, eslint.config.mjs, vitest.config.mts, vitest.setup.ts, .gitignore, .env.example, AGENTS.md, CLAUDE.md}
- frontend/app/{layout.tsx, page.tsx, globals.css, favicon.ico}
- frontend/themes/theme.css
- frontend/shared/config/{api.ts, app.ts, phone.ts, search.ts}
- frontend/shared/features/search/{SearchPage.tsx, SearchForm.tsx, SearchResults.tsx, PhoneCard.tsx, api.ts, schema.ts, *.test.ts(x)}
- frontend/shared/utils/{apiClient.ts, session.ts, routes.ts, apiClient.test.ts}
- frontend/stores/searchStore.ts
- frontend/types/{phone.ts, search.ts}
- frontend/utils/{slug.ts, format.ts, cn.ts, slug.test.ts}
