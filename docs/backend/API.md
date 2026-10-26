# Backend API

Access levels `User` and `Owner`: see [AUTH.md](AUTH.md#access). Data models: [SCHEMAS.md](SCHEMAS.md).

All endpoints are provided by `modules/main` with the `/api` prefix.

Rate limits per module: see [INFRA.md](../INFRA.md#application). An exceeded limit returns 429 with the `Retry-After` header.

| Method | Path | Access | Description | Details |
| --- | --- | --- | --- | --- |
| `POST` | `/api/users` | Public | Create a user, set the session cookie, returns the user with the generated `id` | [AUTH.md](AUTH.md#session-flow) |
| `GET` | `/api/users/me` | User | Get the current user, all fields | [AUTH.md](AUTH.md#session-flow) |
| `PUT` | `/api/users/me` | User | Replace `whatsapp`, `first_name`, `last_name` (validation of `POST /api/users`), returns the user. `id` and `created_at` cannot be changed | [AUTH.md](AUTH.md#session-flow) |
| `GET` | `/api/my-listings` | User | List of the user's listings, newest first: `{"listings": [...]}` | [MY_LISTING.md](../features/MY_LISTING.md) |
| `POST` | `/api/phones/description` | User | Generate the model description and the model data by the model name (LLM). 422: model not found, 503: LLM error | [MY_LISTING.md](../features/MY_LISTING.md#description-response) |
| `POST` | `/api/phones` | User | Create a listing: guardrails, embedding, listing and search index in one transaction with one retry ([DESIGN.md](DESIGN.md#transaction-retry)). 201: the listing, 422: blocked by Guardrail 1 or invalid data, 503: LLM, embedding or database error | [MY_LISTING.md](../features/MY_LISTING.md#add-phone-flow) |
| `PATCH` | `/api/phones/{id}` | Owner | Update a listing: guardrails, listing and search index in one transaction | [MY_LISTING.md](../features/MY_LISTING.md) |
| `DELETE` | `/api/phones/{id}` | Owner | Delete a listing and its search index record in one transaction | [MY_LISTING.md](../features/MY_LISTING.md#delete-phone-flow) |
| `GET` | `/api/phones/{id}` | Public | Listing details, without `user_id` | [PHONE_DETAILS.md](../features/PHONE_DETAILS.md) |
| `GET` | `/api/phones/{id}/contact` | Public | Contact of the listing owner: `whatsapp`, `first_name`, `last_name`, for the Deal button | [PHONE_DETAILS.md](../features/PHONE_DETAILS.md#deal-flow) |
| `POST` | `/api/search` | Public | Search by prompt. Condition and price are taken from the prompt | [RAG.md](../ai/RAG.md) |
| `GET` | `/api/health` | Public | Checks the database connection (`SELECT 1`, timeout 2 seconds): 200 `{"status": "ok"}`, 503 `{"detail": "Database is unavailable"}`. Not rate limited | [DESIGN.md](DESIGN.md#database-connection) |
