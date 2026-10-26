# PLAN — 2026-10-26-phone-details-api

## v1
- P1 `modules/phones/services/crud.py`: `get_phone(session, id) -> PhoneRead | None`; `get_phone_owner_id(session, id) -> UUID | None`. Export in `services/__init__.py`. (R1, R2)
- P2 `modules/users/schemas/user.py`: `UserContact` (whatsapp, first_name, last_name, from_attributes). Export in `schemas/__init__.py`. (R2, A2)
- P3 `modules/main/routers/phones.py`: `GET /{phone_id}` -> `PhoneRead`; `GET /{phone_id}/contact` -> `UserContact`. Both use `DbSession`, parse id as UUID, 404 `Phone not found`. Contact: owner id via P1, user via `users.get_user`, 404 if missing. (R1-R3)
- P4 Tests `modules/main/tests/test_phone_details.py` (test_phones.py is near 261 lines): details, no user_id, contact shape, 404 for malformed/unknown id, 404 on contact of a deleted listing. Service test for P1 in `modules/phones/tests/test_service.py`. (A3)
- P5 Run backend tests; frontend lint/typecheck/test unchanged. (A3, A4)

Risks: route `/{phone_id}` vs `POST /description`: different methods, no conflict.
