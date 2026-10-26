# EXEC — 2026-10-26-eval-structure-by-module

## v1
exec_version: 1

### Changes
- P1: moves: `eval/datasets` -> `eval/rag`; `description.py`, `hallucinated_models.py` -> `eval/phones/`; `targets.py` -> `phones/__init__.py`; `evaluators.py` -> `metrics.py`; `tests/test_evaluators.py` -> `tests/test_metrics.py`. No file left at the old paths.
- P2: `rag/parse.py`, `rag/clarification.py`, `phones/description.py`, `phones/hallucinated_models.py`: case shape, `CASES`, `target`, metrics, `DATASET`; bodies unchanged. Description `os` metric renamed `description.os_match` -> `os_match` inside its file (key `os` unchanged). `metrics.py`: `result`, `valid_output`.
- P3: `rag/__init__.py`, `phones/__init__.py`: `DATASETS`; `run.py`: `DATASETS` registry; `schemas.py`: `EvalDataset.metrics`, `Example`, `Target`, `Metric` only.
- P4: names `<module>.<step>`, table header `Metric`, `Makefile` help `DATASET=rag.parse`.
- P5: tests: imports and names; `test_dataset_name_is_module_dot_step` added.

### Checks
- `ruff check`, `ruff format --check`: pass. DB-free pytest: 54 passed. `pytest --collect-only`: 241. `python -m eval.run --dataset rag.parse` without the key: stops with the documented message.
