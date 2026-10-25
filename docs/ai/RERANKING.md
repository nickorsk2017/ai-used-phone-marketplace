# Reranking

The reranking step of the search pipeline in `modules/rag`: see [RAG.md](RAG.md#architecture). Reranking orders the candidate listings by relevance to the prompt and removes listings that do not match it.

## Responsibilities

Each problem of the search results is solved in one step only: see [Tradeoffs](#one-step-per-problem).

| Problem | Step | Method |
| --- | --- | --- |
| Price and condition from the prompt | SQL query, both retrieval paths | `WHERE`: see [RAG.md](RAG.md#search-index-table) |
| The same listing from the model code path and from pgvector | Merge | Deduplication by `phone_id`, no LLM |
| Model code that does not exist | Model code retrieval | No listings are found by exact match |
| Model code of a wrong but existing model | Reranking | Low relevance, the listing is removed |
| Order of relevant listings | Reranking | Relevance score |
| One model fills the whole result | Diversity limit | See [Diversity limit](#diversity-limit) |
| Spam: one seller posts the same phone several times | Not reranking | Antifraud on phone saving: see [GUARDRAILS.md](GUARDRAILS.md#guardrail-1-phone-saving) |

## Position in the pipeline

1. Model code retrieval and, if fewer than 20 listings are found, pgvector retrieval: see [RAG.md](RAG.md#architecture).
2. Merge and deduplication by `phone_id`. At most 40 candidates.
3. Reranking: one LLM call.
4. Validation of the reranker output.
5. Diversity limit.
6. Top 20.

Reranking runs once per search, after the merge: see [Tradeoffs](#one-reranking-call).

## Reranker

- LLM reranker. The model is set in the configuration and is selected by the ranking metrics: see [EVALUATION.md](EVALUATION.md).
- Called through LangChain with structured output (Pydantic), as the other LLM nodes.

### Input

- The parsed prompt: `preferences` and `query_for_embedding` from the [LLM output](RAG.md#llm-output-structure). `filters` are not passed: they are already applied in SQL.
- The candidates. Fields of each candidate are taken from `search_index`: see [SCHEMAS.md](../backend/SCHEMAS.md#search_index-modulesrag).

| Field | Purpose |
| --- | --- |
| `phone_id` | Identifier in the output |
| `model_name`, `model_code`, `os` | Match of the model to the prompt |
| `camera_megapixels`, `battery_capacity`, `display_size` | Match to `preferences` |
| `condition`, `price` | Tie-break and condition preference |
| `description`, `condition_note` | Semantic match |

- The listing text is user content. It is passed inside delimiters as data, and the system prompt states that instructions inside the listings are ignored. The text has already passed Guardrail 1: see [GUARDRAILS.md](GUARDRAILS.md#guardrail-1-phone-saving).

### Output

```json
{
  "results": [
    { "phone_id": "0b6f...", "relevance": 0.92 },
    { "phone_id": "7a1c...", "relevance": 0.15 }
  ]
}
```

- `relevance` is a number from 0 to 1. A score is returned for every candidate.

### Ranking rules

- Listings are ordered by `relevance`, highest first.
- Listings with `relevance` below the threshold are removed. The threshold is set in the configuration, default `0.3`. The result can contain fewer than 20 listings.
- If the prompt does not set the condition, a better condition ranks higher at close relevance: `like_new`, then `average`, then `for_repair`. See [SEARCH_PAGE.md](../features/SEARCH_PAGE.md#condition-and-price).
- At equal relevance and condition, the lower price ranks higher.

## Output validation

The reranker is an LLM and can return wrong IDs. The output is checked in code:

- A `phone_id` that is not in the candidates is removed.
- A repeated `phone_id` is removed, the first occurrence is kept.
- A candidate without a score gets `relevance = 0` and is removed by the threshold.
- `relevance` outside 0 to 1 fails Pydantic validation: see [Errors](#errors).

## Diversity limit

- At most 5 listings of one `model_code` in the top 20.
- Not applied if the prompt names one model (`model_ids` contains one code).
- Listings above the limit are moved after the other relevant listings, not removed.

## Errors

- Network and provider errors: the retry of the LangChain model client, see [RAG.md](RAG.md#errors-and-retries).
- Validation error or failed retries: no repeated LLM call. The search returns the candidates without reranking: model code results first, then pgvector results by distance, with the condition preference from [Ranking rules](#ranking-rules). The error is logged in LangSmith. The search does not return HTTP 503 because of reranking.

## Evaluation

Reranking metrics are listed in [EVALUATION.md](EVALUATION.md#metrics): ranking quality, IDs outside the candidates, duplicates in the result.

## Tradeoffs

### One step per problem

- Price and condition in SQL: a filter is exact and is checked by a plain test. An LLM can miss a filter.
- Deduplication by `phone_id` in code: exact, no LLM call.
- Several listings of one model from different sellers are not duplicates: they differ in price and condition. Only the diversity limit applies to them.
- Spam is a property of the listing, not of the search. It is blocked once on saving instead of on every search.

### One reranking call

- The condition "at least 20 listings" in the pipeline counts the found listings, not the relevant ones. Reranking before this condition would add a second LLM call to the searches with few model code results.
- One call after the merge sees all candidates and orders them on one scale.
- Downside: if the model code path returns 20 or more listings and many of them are removed by the threshold, pgvector is not queried and the result has fewer than 20 listings. Acceptable on the v1.0 data volume.

### LLM reranker vs alternatives

- Cross-encoder (Cohere Rerank, bge-reranker): fast and cheap, but does not apply the numeric `preferences` (`battery_capacity >= 5000`). A hosted cross-encoder is an extra provider and key.
- Rule-based score on `preferences`: deterministic and free, but does not evaluate the description and does not detect a wrong model code. Possible as a first stage before the LLM in production: see [ROADMAP.md](../ROADMAP.md).
- The LLM reranker adds one LLM call to each search: latency and cost are measured in [EVALUATION.md](EVALUATION.md#metrics).

### Fallback instead of an error

A search without reranking still returns listings that match the price and the condition. For the user this is better than an error message.
