# EXEC — 2026-10-25-frontend-edit-profile

## v1
exec_version: 1

### Changed files
- P1: `frontend/types/user.d.ts`, `frontend/services/UserService.ts` (`update`, PUT).
- P2: `frontend/stores/sessionStore.ts` (`updateProfile`).
- P3: `frontend/features/my-listings/AuthModal.tsx` (optional `user`, edit mode, reset on open).
- P4: `frontend/features/my-listings/ProfileButton.tsx` (new).
- P5: `frontend/features/my-listings/MyListingsPage.tsx`.
- P6: `frontend/services/__test__/UserService.test.ts`, `frontend/features/__test__/my-listings/MyListingsPage.test.tsx`.
- P7: lint, typecheck, test (82 passed), build: pass. Browser check with mocked API: desktop 1100px, mobile 390px.
