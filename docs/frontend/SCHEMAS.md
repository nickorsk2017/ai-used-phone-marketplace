# Frontend Schemas

The Frontend does not own data models. Data models and API contracts are defined by the Backend: [SCHEMAS.md](../backend/SCHEMAS.md), [API.md](../backend/API.md).

- `types/`: TypeScript types of the API, in the same shape as the Backend Pydantic schemas. See [Types](#types).
- Forms and API responses are validated with Zod schemas in `schemas/`.
- Browser storage: `user_id` in `localStorage`, see [AUTH.md](../backend/AUTH.md#session-flow).

## Types

- Types are global ambient declarations in `types/*.d.ts`, one file per entity: `user.d.ts`, `phone.d.ts`, `search.d.ts`, and `requests.d.ts` for the response structure. They are used without imports.
- Types of the API data are inferred from the Zod schemas in `schemas/` with `import("zod").infer<typeof import("@/schemas/...").schema>`. The schema is the single source of the shape. Request bodies that are not validated are declared as interfaces.
- `.d.ts` files in `types/` contain only `declare namespace` blocks, without top-level `import` or `export` (inline `import()` types are allowed): a top-level `import` or `export` turns the file into a module and removes the global types.
- `Entity`: data models, for example `Entity.User`, `Entity.Phone`, `Entity.PhoneCondition`, `Entity.PhoneContact`.
- `Api`: request bodies and response wrappers of the endpoints, for example `Api.CreateUserRequest`, `Api.CreatePhoneRequest`, `Api.SearchResponse`.
- A namespace is split across files: each file adds its entity to `Entity` and its endpoints to `Api`.

## Response

Every service returns `Api.Response<TData>` from `types/requests.d.ts` and does not throw:

- `{ success: true, data, errorText: "" }`: the request succeeded, `data` is validated by the Zod schema of the endpoint.
- `{ success: false, errorText, status }`: the request failed. `errorText` is the Backend `detail` or a default text, `status` is the HTTP status, `0` for a network error.

`utils/apiClient.ts` builds the response and validates the data. A response that does not match the schema is an error with `errorText: "Invalid response"`. Features show their own texts and use `status` to tell errors apart, for example `422` on the description generation.
