# PLAN — 2026-10-26-eval-structure-by-module

## v1
plan_version: 1

### Steps
- P1 (R1, A2): file moves inside the connected folder (no delete permission): `eval/datasets` -> `eval/rag`; `rag/description.py`, `rag/hallucinated_models.py` -> `eval/phones/`; `eval/targets.py` -> `eval/phones/__init__.py`; `eval/evaluators.py` -> `eval/metrics.py`; `tests/test_evaluators.py` -> `tests/test_metrics.py`. Then rewrite the contents.
- P2 (R1, R3): each step file: `CASES`, `target`, its metrics, `DATASET`. Targets and metric bodies copied unchanged. Shared parse-field helpers stay in `rag/parse.py`; `clarification.py` imports `target` from `parse.py`, `hallucinated_models.py` from `description.py`. `metrics.py`: `valid_output`, `result`.
- P3 (R1): `rag/__init__.py`, `phones/__init__.py`: `DATASETS`. `run.py`: registry from both modules keyed by `EvalDataset.name`. `schemas.py`: `evaluators` field -> `metrics`.
- P4 (R2): names `rag.parse`, `rag.clarification`, `phones.description`, `phones.hallucinated_models`; table header `Metric`; `Makefile` help example `DATASET=rag.parse`.
- P5 (A1, A3): tests: imports and names only. Run ruff, DB-free pytest, anchor check.

### Order
P1 -> P2 -> P3 -> P4 -> P5.

### Risks
- Stale `__pycache__` moved with `datasets`: ignored by git, harmless.
- LangSmith datasets of the previous names (`<project>.parse`, ...) stay in LangSmith; the next `make eval` creates the new ones. Old datasets are removed by the Engineer in the LangSmith UI if not needed.
