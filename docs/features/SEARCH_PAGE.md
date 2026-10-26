# Search Page

Route: `/`. The search logic behind the page is described in [RAG.md](../ai/RAG.md).

The page has one `textarea` for the prompt and no filter controls: see [Condition and Price](#condition-and-price).

| Element | Text |
| --- | --- |
| Hint above the field | `Describe the phone you need. It helps to mention the condition (like new, average, for repair), your budget in USD and the brand, if you know it.` |
| Placeholder | `Samsung with a good camera and a long battery life, like new, under $400` |

## Condition and Price

The Search page has no filter controls. Condition and price are taken from the prompt only.

| In the prompt | Condition | Price |
| --- | --- | --- |
| Set explicitly (`like new`, `under 300 dollars`, `400-600`) | SQL filter | SQL filter |
| Not set | No SQL filter. Ranking prefers better condition: `like_new`, then `average`, then `for_repair` | No SQL filter |

- If condition is not set, the result is the 20 most relevant listings, and listings in better condition rank higher. `like_new` is the default preference.
- If price is not set, the `price` field is omitted from the LLM output and from the SQL query (see [RAG.md](../ai/RAG.md#llm-output-structure)).

## Clarification

If the prompt has no phone criteria or asks the assistant for advice, the response has a clarification text instead of listings: see [RAG.md](../ai/RAG.md#clarification).

- The text is shown in place of the listings, in one card of the full width of the results. No listings are shown.
- The prompt stays in the field. The buyer adds the details to the same prompt and sends it again.
- This is not a chat: there is no message history, each request is one prompt and one response.

| Prompt | Shown text |
| --- | --- |
| `What phone should I give my wife for her birthday?` | `What phones does your wife usually like? Describe the budget, the brands and anything else you know: camera, battery, screen size.` |
| `What do you think is better for my wife's birthday, a phone with a good camera or with a good screen?` | An answer about the camera and the screen, then a question about the budget and the brand. |

## Errors

The prompt stays in the field in every case, so the user can send it again.

| Response of `POST /api/search` | Text |
| --- | --- |
| 422: the prompt is blocked by Guardrail 2 ([GUARDRAILS.md](../ai/GUARDRAILS.md#guardrail-2-search-prompt)) | `We could not process this prompt. Please describe the phone in other words.` |
| 429: rate limit ([INFRA.md](../INFRA.md#application)) | `Too many requests. Wait 10 seconds and try again.` |
| Other errors, after the retries ([RAG.md](../ai/RAG.md#errors-and-retries)) | `Something went wrong. Please try again later.` |
