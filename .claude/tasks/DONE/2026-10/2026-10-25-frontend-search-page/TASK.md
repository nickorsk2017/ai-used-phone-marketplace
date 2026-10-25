# TASK — 2026-10-25-frontend-search-page
owner: Engineer
immutable: true

## Requirements
- R1: Scaffold the Frontend application in `frontend/` with the stack of docs/frontend/DESIGN.md#stack and the folder layout of docs/frontend/STRUCTURE.md (including `frontend/CLAUDE.md`).
- R2: Next.js `output: "standalone"` (docs/INFRA.md#server-requirements).
- R3: HeroUI v3 theme in `themes/theme.css`; UI rules of docs/frontend/DESIGN.md#ui (HeroUI tokens only, Tailwind spacing scale only, HeroUI components before custom markup).
- R4: Search page at route `/` per docs/features/SEARCH_PAGE.md: one `textarea`, hint and placeholder texts exactly as specified, no filter controls.
- R5: Route `/` is `noindex` (docs/frontend/DESIGN.md#pages). Route file only composes a component from `shared/features` (docs/frontend/STRUCTURE.md).
- R6: Submit calls `POST /api/search` and renders the returned listings (up to 20). Each result links to `/phones/{id}/{slug}` (docs/features/PHONE_DETAILS.md#route) and shows model name, OS, price in USD, condition, camera, battery, display.
- R7: Error handling per docs/features/SEARCH_PAGE.md#errors: message `Something went wrong. Please try again later.`, the prompt stays in the field.
- R8: API types in `types/` in the shape of docs/backend/SCHEMAS.md#phones-modulesphones, without `user_id` (docs/backend/AUTH.md#access). `X-User-Id` header sent when `user_id` exists in `localStorage` (docs/backend/AUTH.md#access).
- R9: Prompt form with React Hook Form + Zod; search state in a Zustand store in `stores/`.

## Acceptance
- A1: `npm run build`, `npm run lint`, `npm run typecheck` and `npm test` pass in `frontend/`.
- A2: Unit tests cover the prompt schema, the API client (success, error, `X-User-Id`) and the search page states (idle, loading, results, empty, error).
- A3: The rendered `/` page contains the hint, the placeholder, one textarea, a submit button and `<meta name="robots" content="noindex...">`.
- A4: No hex colors and no arbitrary Tailwind values in `frontend/` source files.

## Constraints
- Only English in the repository (CLAUDE.md#2-language).
- Request and response shape of `POST /api/search` is not defined in docs/backend/API.md: use the assumption below and list it as a discrepancy for the Engineer.
  - Request `{ "prompt": string }`, response `{ "results": PhoneListing[] }`.
- Scope: the Search page only. My listings and Phone details pages are out of scope.
