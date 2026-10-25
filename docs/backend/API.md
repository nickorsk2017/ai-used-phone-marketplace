# Backend API

Access levels `User` and `Owner`: see [AUTH.md](AUTH.md#access). Data models: [SCHEMAS.md](SCHEMAS.md).

All endpoints are provided by `modules/main` with the `/api` prefix.

| Method | Path | Access | Description | Details |
| --- | --- | --- | --- | --- |
| `POST` | `/api/users` | Public | Create a user, returns the generated `id` | [AUTH.md](AUTH.md) |
| `GET` | `/api/users/{id}` | Owner | Get user data, all fields | [AUTH.md](AUTH.md) |
| `PUT` | `/api/users/{id}` | Owner | Update user data | [AUTH.md](AUTH.md) |
| `GET` | `/api/my-listings` | Owner | List of the user's listings | [MY_LISTING.md](../features/MY_LISTING.md) |
| `POST` | `/api/phones/description` | User | Generate the model description and the model data by the model name (LLM) | [MY_LISTING.md](../features/MY_LISTING.md#description-response) |
| `POST` | `/api/phones` | User | Create a listing: guardrails, embedding, listing and search index in one transaction | [MY_LISTING.md](../features/MY_LISTING.md#add-phone-flow) |
| `PATCH` | `/api/phones/{id}` | Owner | Update a listing: guardrails, listing and search index in one transaction | [MY_LISTING.md](../features/MY_LISTING.md) |
| `DELETE` | `/api/phones/{id}` | Owner | Delete a listing and its search index record in one transaction | [MY_LISTING.md](../features/MY_LISTING.md#delete-phone-flow) |
| `GET` | `/api/phones/{id}` | Public | Listing details, without `user_id` | [PHONE_DETAILS.md](../features/PHONE_DETAILS.md) |
| `GET` | `/api/phones/{id}/contact` | Public | Contact of the listing owner: `whatsapp`, `first_name`, `last_name`, for the Deal button | [PHONE_DETAILS.md](../features/PHONE_DETAILS.md#deal-flow) |
| `POST` | `/api/search` | Public | Search by prompt. Condition and price are taken from the prompt | [RAG.md](../ai/RAG.md) |
