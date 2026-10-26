# TASK — 2026-10-26-seed-chinese-brands
owner: Engineer
immutable: true

## Requirements
- R1: Add 30 seed listings of Xiaomi (incl. POCO), Huawei, Oppo, vivo, Honor, Realme and Nothing (incl. CMF) models released in 2025 and 2026, one listing per model, with real model data.
- R2: docs describe the new seed size and the model code of models without a US version.

## Acceptance
- A1: `seed.run.LISTINGS` has 90 listings, `check_listings()` passes, every listing validates as `PhoneCreate`.
- A2: All 7 brands are present, all three conditions are used, every listing references an existing seed user.
- A3: docs/ (STRUCTURE.md, EVALUATION.md, DESIGN.md, RAG.md) and README.md state 90 listings and the model code rule; no other mention of 60 listings remains.
- A4: ruff passes on `backend/seed`, existing backend unit tests pass.

## Constraints
- No schema, API or prompt changes.
