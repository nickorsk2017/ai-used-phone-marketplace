# PLAN — 2026-10-25-frontend-header-profile

## v1
plan_version: 1

### Steps
- P1 (R2): `stores/sessionStore.ts`: `init` reuses the pending request.
- P2 (R1): `ui/layouts/AppHeader.tsx`: optional `actions` slot after `nav`.
- P3 (R1-R3): `features/profile/HeaderProfile.tsx` (init on mount, `ProfileButton` + `AuthModal` with `user`), `ProfileButton.tsx` moves from `features/my-listings/` to `features/profile/`.
- P4 (R1): `app/layout.tsx` passes `<HeaderProfile />`. `MyListingsPage.tsx` restores the single "Add new phone" button.
- P5 (A2): `features/__test__/profile/HeaderProfile.test.tsx`, edit profile tests move there from `MyListingsPage.test.tsx`.
- P6 (A1): lint, typecheck, test, build.
- P7 (R4): `MyListingsList.tsx` drops the empty state button and the `onAdd` prop; `MyListingsPage.tsx` stops passing it.
