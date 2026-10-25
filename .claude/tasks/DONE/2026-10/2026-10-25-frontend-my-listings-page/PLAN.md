# PLAN — 2026-10-25-frontend-my-listings-page

## v1
plan_version: 1

### Steps
- P1 (R1): `app/my-listings/page.tsx`: `metadata.robots = { index: false, follow: true }`, renders `MyListingsPage` from `shared/features/my-listings/`.
- P2 (R9): `shared/ui/AppHeader.tsx` (`"use client"`, active link by pathname) in `app/layout.tsx`. Nav texts in `shared/config/app.ts`.
- P3 (R4, R6, R7): `PhoneCard` moves to `shared/ui/PhoneCard.tsx` (used by Search and My listings), optional `actions` slot above the stretched link. Search imports updated.
- P4 (R2-R4, R6, R7): `types/user.ts` (`User`, `CreateUserRequest`), `types/phone.ts` adds `PhoneDescription`, `CreatePhoneRequest`, `MyListingsResponse`.
- P5 (R2-R7): `shared/utils/session.ts` adds `setUserId`, `clearUserId`. `shared/utils/apiClient.ts` handles 204 without body. API functions in `shared/features/my-listings/api.ts`.
- P6 (R5): `shared/utils/guardrails.ts`: regex checks for card numbers (13-19 digits with separators, Luhn), phone numbers (7+ digits with separators, US formats), links (scheme, `www.`, domain with a TLD). Returns the found categories.
- P7 (R8): `shared/features/my-listings/schemas.ts`: user schema (WhatsApp in international format, names), model name schema, listing schema (positive numbers, condition enum, positive integer price, guardrail refinement on description and condition note).
- P8 (R2, R3, R6, R7): `stores/sessionStore.ts` (`status`: checking | anonymous | ready | error, `user`, `init`, `createUser`); `stores/myListingsStore.ts` (`status`, `listings`, `load`, `add`, `remove`).
- P9 (R2): `CreateUserModal.tsx`.
- P10 (R4-R6): `AddPhoneModal.tsx`: step 1 model name + Generate; step 2 generated data, condition note, condition, price, Publish. Changing the model name after generation clears the generated data. Errors: 422 next to the model name, guardrail errors next to the field, save error as an Alert with the form kept.
- P11 (R3, R7): `MyListingsList.tsx` (loading, empty, error with retry, cards with Delete), `DeletePhoneDialog.tsx` (HeroUI AlertDialog).
- P12 (R1-R7): `MyListingsPage.tsx` composition. Texts in `shared/config/my-listings.ts`.
- P13 (A2, A5): tests next to the modules.
- P14 (A1, A3, A4): lint, typecheck, tests, build, grep checks, browser check with a mocked API.

### Risks
- API bodies are assumptions (TASK constraint): isolated in `types/` and `api.ts`.
- Texts not in docs (empty list, delete confirmation, guardrail error, save error, form labels): `shared/config/my-listings.ts`, listed as discrepancies.
