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

## Errors

If `POST /api/search` returns an error after the retries ([RAG.md](../ai/RAG.md#errors-and-retries)), the page shows `Something went wrong. Please try again later.` The prompt stays in the field, so the user can send it again.
