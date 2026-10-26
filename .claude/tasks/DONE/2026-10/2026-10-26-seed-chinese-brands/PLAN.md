# PLAN — 2026-10-26-seed-chinese-brands

## v1
plan_version: 1

### Steps
- S1 (R2): docs first. STRUCTURE.md#seed: files `seed_4.py` (14), `seed_5.py` (16); model code rule: US code, else global code, else China code. RAG.md#model-code-limitations: models without a US version. EVALUATION.md#data, DESIGN.md, README.md: 90 listings.
- S2 (R1): `backend/seed/listing/seed_4.py`: Xiaomi, POCO, Huawei, Honor (14). `seed_5.py`: Oppo, vivo, Realme, Nothing, CMF (16). Format of `seed_3.py`. `camera_megapixels` = main wide camera; foldables: main display; battery of the version of the model code.
- S3 (R1): `seed/run.py` imports `seed_4`, `seed_5` into `LISTINGS`. `listing/__init__.py` docstring without the per-file count.

### Risks
- Model codes of non-US models may differ from the code the search LLM returns: vector search covers it (RAG.md#architecture step 4).
