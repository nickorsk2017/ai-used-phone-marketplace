# EXEC — 2026-10-25-frontend-header-profile

## v1
exec_version: 1

### Changed files
- P1: `frontend/stores/sessionStore.ts`.
- P2: `frontend/ui/layouts/AppHeader.tsx`.
- P3: `frontend/features/profile/HeaderProfile.tsx` (new), `frontend/features/profile/ProfileButton.tsx` (moved).
- P4: `frontend/app/layout.tsx`, `frontend/features/my-listings/MyListingsPage.tsx`.
- P5: `frontend/features/__test__/profile/HeaderProfile.test.tsx` (new), `frontend/features/__test__/my-listings/MyListingsPage.test.tsx`, `frontend/features/__test__/my-listings/AddPhoneModal.test.tsx`.
- P7: `frontend/features/my-listings/MyListingsList.tsx`.
- P6: lint, typecheck, test (17 files, 83 tests), build: pass. Browser check with mocked API: header profile on Search and My listings, desktop and mobile.
