# EXEC — 2026-10-25-frontend-phone-details-page

## v1
exec_version: 1

### Summary
- P1: `API_STUB_ENABLED` (`NEXT_PUBLIC_API_STUB`), `SITE_URL` (`NEXT_PUBLIC_SITE_URL`, default `http://localhost:3000`). Local `.env` (gitignored) with the stub on.
- P3: `display_size` coerced (Pydantic decimal may serialize as a string); unknown fields such as `user_id` are stripped.
- P4: 3 stub listings (like_new, average, for_repair) with fixed UUIDs. `getPhone`: 404 and 422 -> `null`.
- P5: `og:type = product` is not supported by the Next.js Metadata API: rendered as `<meta property>` in the page, React hoists it into `<head>`. Title uses `absolute` to bypass the layout template.
- P7: condition badge as server markup with HeroUI `chipVariants` (`shared/ui/ConditionBadge.tsx`): HeroUI `Chip` is a Client Component. Modal also shows the seller name from the contact response.
- P9: 19 tests, 6 files. Full suite: 65 tests, 13 files.
- P10: lint, typecheck, test, build pass. `next start` with the stub: HTML contains all content and JSON-LD, no WhatsApp number; wrong slug 308; unknown id 404; robots.txt as specified; `Cache-Control: s-maxage=60`. Browser check: modal, copy to clipboard, "Copied", no console errors.

### Changed files
- frontend/{.env.example, .env}
- frontend/app/{layout.tsx, robots.ts, phones/[id]/[slug]/page.tsx}
- frontend/shared/config/{api.ts, phone-details.ts}
- frontend/shared/ui/ConditionBadge.tsx
- frontend/shared/features/phone-details/{api.ts, stub.ts, schema.ts, seo.ts, loadPhonePage.ts, PhoneDetailsPage.tsx, DealButton.tsx, testPhone.ts, *.test.ts(x)}
- frontend/types/phone.ts
