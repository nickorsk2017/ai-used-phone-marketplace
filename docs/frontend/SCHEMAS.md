# Frontend Schemas

The Frontend does not own data models. Data models and API contracts are defined by the Backend: [SCHEMAS.md](../backend/SCHEMAS.md), [API.md](../backend/API.md).

- `types/`: TypeScript types of the API responses, in the same shape as the Backend Pydantic schemas.
- Forms are validated with Zod.
- Browser storage: `user_id` in `localStorage`, see [AUTH.md](../backend/AUTH.md#session-flow).
