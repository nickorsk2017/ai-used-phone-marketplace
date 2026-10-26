# Frontend Architecture

Folders and files: [STRUCTURE.md](STRUCTURE.md). Types, form validation and browser storage: [SCHEMAS.md](SCHEMAS.md). System architecture: [BRIEF.md](../../BRIEF.md).

## Stack

- React
- Next.js
- TypeScript
- React Hook Form
- Zod
- Tailwind CSS
- HeroUI v3
- Zustand

## Pages

| Route | Page | Rendering | Indexing | Specification |
| --- | --- | --- | --- | --- |
| `/` | Search | Client Component | `noindex` | [SEARCH_PAGE.md](../features/SEARCH_PAGE.md) |
| `/my-listings` | My listings | Client Component | `noindex` | [MY_LISTING.md](../features/MY_LISTING.md) |
| `/phones/[id]` | Phone details | Server Component, ISR | indexed | [PHONE_DETAILS.md](../features/PHONE_DETAILS.md) |

Page requirements: see [TASK.md](../TASK.md#business-requirements).

## Rendering

- Server Components by default.
- `"use client"` only for components with state, event handlers or browser APIs.
- Search and My listings depend on the user session and the prompt, so they are rendered on the client.
- Phone details: see [PHONE_DETAILS.md](../features/PHONE_DETAILS.md#rendering).

## UI

- HeroUI v3 is the UI component library: see [Tradeoffs](#heroui).
- The theme is generated with the HeroUI Theme Builder and stored in `themes/theme.css`.
- Colors, border radius, borders and shadows come only from HeroUI tokens in `themes/theme.css`. Hex values in components are not allowed.
- Spacing uses only the Tailwind scale. Arbitrary values such as `p-[13px]` are not allowed.
- If HeroUI has a component for the task, it is used instead of custom markup in `ui`.
- Feature modals are built on `ui/organisms/modal/Modal` ([STRUCTURE.md](STRUCTURE.md)), not on HeroUI `Modal` directly. Confirmation dialogs use HeroUI `AlertDialog`.
- Form fields in features use the inputs of `ui/molecules/forms` (`TextField`, `NumberField`, `Select`).
- Page texts are static strings in the JSX of the components. i18n is not used: see [Tradeoffs](#i18n).

## Errors

- `app/error.tsx` is the error boundary of all routes. It shows `Something went wrong. Please try again later.` and a "Try again" button that re-fetches and re-renders the route.
- A missing listing is not an error: see [PHONE_DETAILS.md](../features/PHONE_DETAILS.md#errors).

## Tradeoffs

### HeroUI

[TASK.md](../TASK.md#out-of-scope-for-v10) requires ready-made UI components instead of custom ones. HeroUI is the chosen library.

### i18n

v1.0 targets the US market only, so the UI has one language. Texts are written directly in the JSX instead of translation keys. A second market requires i18n: texts move to message files with keys.
