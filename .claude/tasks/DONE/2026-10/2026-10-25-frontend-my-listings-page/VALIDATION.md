# VALIDATION — 2026-10-25-frontend-my-listings-page

## v2
validation_version: 2
result: PASS

### Checks
- A1: lint, typecheck, test (46), build: PASS.
- A2: PASS (user schema, listing schema, guardrail regex, session flow x4, add flow x4, delete).
- A3: PASS. A4: PASS. A5: PASS (Search tests unchanged and green).
- R1-R9: PASS in Chromium with a mocked API at 1280 px and 390 px; V1-1 fixed.
- 404 in the browser console come from Link prefetch of `/phones/{id}/{slug}`: the Phone details page is not implemented yet.

### Discrepancies (CLAUDE.md#1)
- D1: docs/backend/API.md defines no bodies of `POST /api/users`, `GET /api/users/{id}`, `GET /api/my-listings`, `POST /api/phones/description`, `POST /api/phones`, `DELETE /api/phones/{id}`. Code assumptions: TASK.md constraints, frontend/types/{user,phone}.ts. Fix: add request/response schemas to API.md.
- D2: docs/features/MY_LISTING.md does not define the response of `POST /api/phones` when Guardrail 1 blocks the listing (status, message). Code: HTTP 422 -> `ADD_PHONE_TEXTS.rejected`. Fix: add to MY_LISTING.md or GUARDRAILS.md.
- D3: docs/ai/GUARDRAILS.md#guardrail-1-phone-saving names the Frontend Regex categories but not the patterns. Code: frontend/shared/utils/guardrails.ts (Luhn for cards, 7-15 digits for phones, URL/e-mail/domain for links). Backend Regex must use the same rules. Fix: describe the patterns in GUARDRAILS.md (one source for both layers).
- D4: docs/features/MY_LISTING.md has no texts for the page, the user modal, form labels, the empty list, the delete confirmation and the save errors. Code: frontend/shared/config/my-listings.ts. Fix: add an Elements table.
- D5: docs/backend/SCHEMAS.md#users-modulesauth does not define the WhatsApp format. Code: international format `+<7-15 digits>`, normalized before `POST /api/users`. Fix: add the format to SCHEMAS.md.
- D6: MY_LISTING.md step 5 does not say whether the condition note is required. Code: optional. Fix: state it in MY_LISTING.md.
- D7: API.md lists `PATCH /api/phones/{id}` and `PUT /api/users/{id}`, MY_LISTING.md has no edit UI. Not implemented. Fix: add an Edit flow to MY_LISTING.md or mark the endpoints as API-only.
- D8: docs/frontend/DESIGN.md#pages has no navigation between pages. Code: header with Search and My listings (frontend/shared/ui/AppHeader.tsx). Fix: add the header to DESIGN.md.

## v1
validation_version: 1
result: FAIL

### Checks
- A1: clean `npm ci`, lint, typecheck, test (46), build: PASS.
- A3: PASS (`noindex, nofollow`). A4: PASS. A5: PASS.
- Browser (Chromium, mocked API): user creation, list, generate, guardrail block, publish, delete: PASS at 1280 px.

### Issues
- {id: V1-1, type: logic, severity: low, ref: R9, note: "frontend/shared/ui/AppHeader.tsx: at 390 px the app name and the `My listings` nav item wrap to two lines."}
