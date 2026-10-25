# AI Architecture

AI components of the system: models, orchestration, vector search, guardrails and evaluation. Backend code and modules: [backend/DESIGN.md](../backend/DESIGN.md). Where AI is used and where it is not: [TASK.md](../TASK.md#where-ai-fits-and-where-it-does-not).

| Document | Content |
| --- | --- |
| [RAG.md](RAG.md) | Search: hybrid RAG, LangGraph pipeline, LLM output, model code, vector index |
| [RERANKING.md](RERANKING.md) | Reranking of the search results: LLM reranker, output validation, diversity limit, fallback |
| [GUARDRAILS.md](GUARDRAILS.md) | Toxic content, fraud and Prompt Injection protection of listings, Prompt Injection protection of search |
| [EVALUATION.md](EVALUATION.md) | Evaluation, Observability and cost of the LLM calls |

## Stack

- OpenAI: LLM and embeddings in v1.0.
- LangChain is the provider-agnostic interface for chat models and embeddings: see [Tradeoffs](#langchain-and-the-model-provider).
- LangGraph orchestrates the search pipeline: see [RAG.md](RAG.md#orchestration-langgraph).
- pgvector in PostgreSQL (Supabase) for the vector index (rationale: [RAG.md](RAG.md#pgvector-vs-a-dedicated-search-engine)).
- DeepEval and LangSmith for Evaluation, Observability and cost: see [EVALUATION.md](EVALUATION.md).

## AI in the Backend modules

- `modules/phones`: generation of the model description and the model data (LLM), Guardrail 1 for phone saving: see [GUARDRAILS.md](GUARDRAILS.md#guardrail-1-phone-saving).
  - Phone model data (model code, OS, camera, battery, display) is taken from the LLM when the listing is created. A separate model catalog is not maintained in v1.0. Model code rules and limitations: see [RAG.md](RAG.md#model-code). Errors are detected through user feedback and evaluation: see [EVALUATION.md](EVALUATION.md).
- `modules/rag`: query parsing, model codes, embeddings, vector search and reranking: see [RAG.md](RAG.md). Guardrail 2 for the search prompt: see [GUARDRAILS.md](GUARDRAILS.md#guardrail-2-search-prompt).

## Tradeoffs

### LangChain and the model provider

v1.0 uses OpenAI, but OpenAI is not assumed to be the best model for every task. The provider (Gemini, Gemma, Llama and others) is changed in the configuration, without changes in the pipeline code. Changing the embedding model requires reindexing all listings. Before real users this is not critical: the data is synthetic. The chat model and the embedding model are selected after collecting metrics with the AI model router: see [ROADMAP.md](../ROADMAP.md#production-baseline).
