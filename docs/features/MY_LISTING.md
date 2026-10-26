# My Listing

The page requires a user. If there is no user in the browser session, the page first shows the user creation modal window: see [AUTH.md](../backend/AUTH.md#session-flow). The modal window has the title `Create your seller profile`. If `POST /api/users` fails, the form stays filled and shows `Could not create the profile. Please try again.`

## Edit Profile Flow

1. When the user is loaded, the application header shows the user avatar with the initials and the full name after the navigation links, on every page. The "Add new phone" button stays in the My listings page header.
2. The user clicks the avatar or the name. The user modal window of the [Session Flow](../backend/AUTH.md#session-flow) opens with the current values, the title `Edit your seller profile`, a close button and the "Save" button.
3. The form is validated with the same rules as the user creation.
4. The Frontend calls `PUT /api/users/me` with `whatsapp`, `first_name` and `last_name`: see [API.md](../backend/API.md).
5. On success the header shows the updated name and the modal window closes. On error the form stays filled and shows `Could not save the profile. Please try again.`

## Add Phone Flow

1. The user clicks the "Add new phone" button in the page header. It is the only "Add new phone" button: the empty list shows only the text `You have no listings yet. Add your first phone for sale.`
2. The user enters the model name.
3. The Frontend calls `POST /api/phones/description`. The LLM returns the description and the model data: see [Description Response](#description-response).
4. The user reviews the generated data and can edit the description and the specifications (camera, battery, display). The model name and the OS are not editable. The model code is not shown.
5. The user fills in notes about the phone's condition, for example: "There are scuffs and scratches".
6. The user selects the Condition value from a list: like new (`like_new`), average condition (`average`), for repair (`for_repair`).
7. The user enters the price in USD (positive integer).
8. The user clicks "Publish". The Frontend calls `POST /api/phones`. Guardrail 1 checks the listing for toxic content, fraud and Prompt Injection before saving: see [GUARDRAILS.md](../ai/GUARDRAILS.md#guardrail-1-phone-saving). A blocked listing returns HTTP 422, the form stays filled and shows `The listing was not accepted. The description and the condition note may only describe the phone model and its condition. Phone numbers, websites and other contact details are not allowed.`
9. The embedding of the listing text is generated (OpenAI).
10. The listing record and its search index record are created in one PostgreSQL transaction. A transient database error is retried once: see [DESIGN.md](../backend/DESIGN.md#transaction-retry). If the embedding or both attempts fail, nothing is saved, the Backend returns HTTP 503, the form stays filled and shows `The listing was not saved. Please try again.` The user sends the same form again with "Publish".
11. On success the modal window closes and the Frontend loads the list again with `GET /api/my-listings`.

Rate limits of `POST /api/phones/description` and `POST /api/phones`: see [INFRA.md](../INFRA.md#application). On HTTP 429 the modal window keeps the entered data and shows `Too many requests. Wait 10 seconds and try again.`

## Description Response

`POST /api/phones/description` returns the description and the structured model data. Field types: see [SCHEMAS.md](../backend/SCHEMAS.md#phones-modulesphones). Model code rules: see [RAG.md](../ai/RAG.md#model-code).

```json
{
  "model_code": "A2483",
  "model_name": "iPhone 13 Pro",
  "os": "ios",
  "camera_megapixels": 12,
  "battery_capacity": 3095,
  "display_size": 6.1,
  "description": "iPhone 13 Pro with a 6.1-inch ProMotion display, A15 Bionic chip and a triple 12 MP camera system."
}
```

- `description`, `camera_megapixels`, `battery_capacity` and `display_size` are shown in editable fields. The edited values are saved with the listing. The specifications are validated as positive numbers (Zod on the Frontend, Pydantic on the Backend).
- `model_name` and `os` are shown read-only and are saved as returned.
- `model_code` is not shown in the UI and is saved as returned. It links the listing to the search: see [Tradeoffs](#hidden-model-code).
- The LLM output has the field `model_found`. If the LLM does not find the model (`model_found: false`), the endpoint returns HTTP 422 and no description. The Frontend shows the error `Model not found. Check that the model really exists.` next to the model name field, and the user can correct the name and try again.

## Delete Phone Flow

When a phone is deleted, the listing record and its search index record are deleted in one PostgreSQL transaction.

## Tradeoffs

### Hidden model code

The model code from the LLM is a temporary v1.0 (PoC) solution. It is hidden from the seller because a wrong manual change would break the search by model code. In production the model is selected from the model catalog: see [RAG.md](../ai/RAG.md#production-model-catalog).
