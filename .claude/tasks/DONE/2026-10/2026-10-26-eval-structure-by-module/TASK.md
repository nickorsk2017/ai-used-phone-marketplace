# TASK — 2026-10-26-eval-structure-by-module
owner: Engineer
immutable: true

## Requirements
- R1: `backend/eval/` layout per docs/backend/STRUCTURE.md#eval: `rag/` and `phones/` folders, one file per step with its cases, target and metrics, `DATASETS` per module, shared `metrics.py`.
- R2: Dataset names `<module>.<step>` per docs/ai/EVALUATION.md#datasets; `make eval DATASET=rag.parse` per docs/ai/EVALUATION.md#run; table column `Metric`.
- R3: No change of the cases, the targets or the metric logic.

## Acceptance
- A1: `ruff check`, `ruff format --check` pass. `eval/tests` and the tracing tests pass without database.
- A2: `eval/datasets/`, `eval/targets.py`, `eval/evaluators.py` no longer exist; no import of them remains.
- A3: Same cases and metric results as before: the existing tests pass with updated imports and names only.
- A4: All Markdown anchor links changed by the task resolve.

## Constraints
- docs/ are already updated and are the source of truth for this task.
- `make eval` is not run (CLAUDE.md#validator).
