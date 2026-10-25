# Frontend Structure

Architecture and rendering rules: [DESIGN.md](DESIGN.md).

```
frontend/
  app/
  config/
  features/
  mocks/
  public/
  schemas/
  services/
    stubs/
  stores/
  themes/
    theme.css
  types/
  ui/
    layouts/
    molecules/
      forms/
    organisms/
      modal/
  utils/
  CLAUDE.md
  .env
```

- `app`: Next.js App Router routes. Route files only compose components from `features`.
- `config`: application constants and settings: API, application name and navigation, labels of the phone enums.
- `features`: feature modules, one folder per page. Helpers used by one feature stay in its folder.
- `mocks`: test data and helpers shared by tests: `testPhone`, `testPhoneDescription`, `testListing`, `testUser`, `jsonResponse`, `mockApi` (`fetch` stub with handlers by method and path).
- `public`: static files.
- `schemas`: Zod schemas, one file per schema group: API responses validated by the services (`phoneSchemas`, `userSchemas`, `searchSchemas`) and form schemas (`searchFormSchema`, `myListingsFormSchemas`).
- `services`: one service per entity, for example `UserService`, `PhoneService`, `SearchService`, and `AuthService` for the browser session and registration. A service contains the API calls of the entity and the operations on it, and returns `Api.Response`: [SCHEMAS.md](SCHEMAS.md#response). Features and stores call services, not `utils/apiClient.ts` directly.
  - `stubs`: stub API data enabled by `NEXT_PUBLIC_API_STUB=true`.
- `stores`: Zustand stores.
- `themes`: HeroUI theme, CSS variables.
- `types`: global TypeScript types in `.d.ts` files, namespaces `Entity` and `Api`: [SCHEMAS.md](SCHEMAS.md#types).
- `ui`: reusable UI components built on HeroUI, grouped by Atomic Design levels.
  - `layouts`: application and page layout: `AppHeader`, `PageContainer` (the `<main>` wrapper of every page).
  - `molecules`: `Alert`, `CardSkeletonGrid`, `ConditionBadge`, `SpecList`.
  - `molecules/forms`: form inputs bound to React Hook Form: `TextField`, `NumberField`, `Select`.
  - `organisms`: `PhoneCard`.
  - `organisms/modal`: `Modal`, the base of every feature modal.
- `utils`: general helpers: API client, session, routes, class names, text formatting, phone specifications for `SpecList` (`phoneSpecs.ts`), `guardrails.ts` (Frontend Regex layer: [GUARDRAILS.md](../ai/GUARDRAILS.md)).
- `CLAUDE.md`: rules for AI coding agents working in the Frontend.
- `.env`: environment variables.

## Tests

- Each module folder (`features`, `schemas`, `services`, `stores`, `ui`, `utils`) keeps its tests in its own `__test__/` folder: `<name>.test.ts(x)`. Inside `__test__/` the path repeats the module tree, for example `features/__test__/search/SearchPage.test.tsx` tests `features/search/SearchPage.tsx`.
- Test data lives in `mocks/`.
