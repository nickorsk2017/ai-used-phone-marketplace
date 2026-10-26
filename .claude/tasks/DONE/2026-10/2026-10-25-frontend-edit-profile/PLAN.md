# PLAN — 2026-10-25-frontend-edit-profile

## v1
plan_version: 1

### Steps
- P1 (R3): `types/user.d.ts` adds `Api.UpdateUserRequest`. `UserService.update(id, body)`: `PUT /api/users/{id}`, `userSchema`.
- P2 (R3): `stores/sessionStore.ts` adds `updateProfile(body)`: calls `UserService.update` with the session user id, replaces `user` on success, returns `Api.Response`.
- P3 (R2, R3): `AuthModal.tsx` takes optional `user`. With `user`: edit mode (title, close button, "Save", current values reset on open, `updateProfile`, edit error text). Without `user`: creation unchanged.
- P4 (R1): `features/my-listings/ProfileButton.tsx`: HeroUI `Button` (ghost) with `Avatar` initials and the full name, `aria-label="Edit profile"`.
- P5 (R1, R2): `MyListingsPage.tsx`: `ProfileButton` next to "Add new phone" when ready, second `AuthModal` instance with `user` for editing.
- P6 (A2): tests in `services/__test__/UserService.test.ts` and `features/__test__/my-listings/MyListingsPage.test.tsx`.
- P7 (A1): lint, typecheck, test, build.

### Risks
- HeroUI modal keeps form state between openings: reset on open in P3.
