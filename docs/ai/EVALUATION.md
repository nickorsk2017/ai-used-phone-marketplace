# EVALUATION.md

Evaluation, Observability and cost of the LLM calls. Stack: see [DESIGN.md](DESIGN.md#stack).

v1.0 evaluates the steps where AI can fail regardless of the data volume: prompt parsing, model data generation, guardrails and filters. Ranking quality is evaluated as an estimate only: see [Tradeoffs](#what-is-not-measured-in-v10).

## Data

- Seed: about 50 synthetic listings, mostly of different models, plus a few listings of the same model with different condition and price.
- Test sets: 10 to 20 cases per group. This is a regression set, not a statistical benchmark.

## Metrics

| Step | Metric | Target | Tool |
| --- | --- | --- | --- |
| Prompt parsing: see [RAG.md](RAG.md#llm-output-structure) | Share of prompts where condition, price and OS match the expected values. Share of valid JSON | 100% valid JSON | LangSmith |
| Filters in the results | Share of results that violate the price or the condition from the prompt | 0% | Plain test |
| Model data generation: see [MY_LISTING.md](../features/MY_LISTING.md#description-response) | Share of cases where `model_code` and `os` match the expected values and the specifications are close to them. Share of valid JSON | 100% valid JSON | LangSmith |
| Hallucinated models | A model that does not exist (for example, `iPhone 25`) returns HTTP 422 and no description | 100% | LangSmith |
| Guardrails: see [GUARDRAILS.md](GUARDRAILS.md) | Share of blocked toxic, fraud and prompt injection cases. Share of false blocks of clean texts | All bad cases blocked, no false blocks | Plain test |
| Reranker output: see [RERANKING.md](RERANKING.md#output-validation) | Share of reranker IDs that are not in the candidates. Share of results with a repeated `phone_id` | 0% in the result | Plain test |
| Latency and cost | p50 and p95 of the search time, cost of a search and of a listing creation | Measured, no target in v1.0 | LangSmith |
| Ranking | `ContextualRelevancyMetric` (share of relevant results) and `ContextualPrecisionMetric` (relevant results ranked higher) on the top 5 results | Estimate only | DeepEval, LLM judge |

## LangSmith

- Each LLM call is traced: prompt, response, latency, tokens and cost. In the search pipeline each LangGraph node is a separate span: see [RAG.md](RAG.md#orchestration-langgraph).
- Errors of the LLM calls and retries are visible in the traces: see [RAG.md](RAG.md#errors-and-retries).
- The datasets of prompt parsing and model data generation are stored in LangSmith. Runs are compared after a prompt or model change.

## DeepEval

- Each test case: the prompt, the top 5 search results and `expected_output` (one sentence that describes the ideal result, for example `Android phones under $300 with a battery of 5000 mAh or more`).
- The judge model is set in the configuration. Default: OpenAI. The provider can be changed in the configuration, for example to a local model through Ollama.

## Run

`make eval` runs the LangSmith evaluations, the DeepEval metrics and the plain tests, and prints a results table.

## Results

To be filled after the implementation.

## Tradeoffs

### What is not measured in v1.0

- Recall: the LLM judge sees only the returned results, not the relevant listings that the search missed.
- Statistical quality of the search: 10 to 20 prompts on about 50 synthetic listings catch regressions but do not measure the quality level. For many prompts only a few listings are relevant, so ranking metrics are an estimate.
- Behavior on real prompts and online metrics (clicks on results, Phone details views and Deal clicks after a search): after the first users, see [ROADMAP.md](../ROADMAP.md#production-baseline).

### LLM judge instead of labeled relevant listings

- No labels are needed: the judge evaluates the results that the search returns now. Sold and new listings do not break the test set.
- Downside: the judge result varies slightly between runs, and Recall cannot be measured.

### Top 5 instead of all 20 results

The top 5 is the first screen that the user sees. On a small dataset many prompts have fewer than 20 relevant listings, so the score of all 20 results would be low even for a correct search.

### LangSmith for generation, DeepEval for ranking

- LangSmith already traces every LLM call. Datasets and evaluators of the generation steps work on the same traces.
- DeepEval provides ready LLM judge metrics for retrieval.
