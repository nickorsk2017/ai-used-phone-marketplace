# EXEC — 2026-10-25-frontend-my-listings-page

## v2
exec_version: 2

### Summary
- V1-1: header app name truncates, nav items `whitespace-nowrap`, smaller padding below `sm`. Read-only model name and OS use `text-foreground`.

### Changed files
- frontend/shared/ui/AppHeader.tsx
- frontend/shared/features/my-listings/AddPhoneModal.tsx

## v1
exec_version: 1

### Summary
- P1: route `/my-listings`, `noindex, nofollow`. Root `metadata.title` uses a template.
- P2: `AppHeader` in the root layout. Search page eyebrow with the app name removed: the header shows it.
- P3: `PhoneCard` moved to `shared/ui`, `actions` slot (`relative z-10` above the stretched link).
- P5: `apiClient` returns `undefined` for 204.
- P6: card = 13-19 digits passing Luhn, or 16-19 digits; phone = 7-15 digits; links = scheme, `www.`, e-mail, short links, domain with a common TLD. Commas are not separators, so `5,000 mAh` passes.
- P7: WhatsApp normalized to `+<digits>` (7-15 digits). Condition note optional.
- P8: `sessionStore`, `myListingsStore`. The user modal is derived from `status === "anonymous"` (no setState in effects).
- P10: Backend 422 on save is shown as a rejection text (Guardrail 1), other errors as a retry text; form data kept. Backdrop click does not close the add modal.
- P13: 46 tests in 7 files (24 new for My listings).

### Changed files
- frontend/app/{layout.tsx, my-listings/page.tsx}
- frontend/shared/config/{app.ts, my-listings.ts}
- frontend/shared/ui/{AppHeader.tsx, PhoneCard.tsx} (PhoneCard moved from shared/features/search/)
- frontend/shared/features/search/{SearchPage.tsx, SearchResults.tsx}
- frontend/shared/features/my-listings/{MyListingsPage.tsx, MyListingsList.tsx, CreateUserModal.tsx, AddPhoneModal.tsx, DeletePhoneDialog.tsx, api.ts, schemas.ts, schemas.test.ts, MyListingsPage.test.tsx}
- frontend/shared/utils/{apiClient.ts, session.ts, guardrails.ts, guardrails.test.ts}
- frontend/stores/{sessionStore.ts, myListingsStore.ts}
- frontend/types/{phone.ts, user.ts}
