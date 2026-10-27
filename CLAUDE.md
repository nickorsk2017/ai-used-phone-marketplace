# CLAUDE.md

Rules for AI coding agents working in this repository.

## 1. Documentation is the source of truth

- Documentation is the primary source of truth for this project.
- The `docs/` folder describes every module of the system:
  - `docs/`: system-level documents: product, architecture, infrastructure, roadmap.
  - `docs/backend/` and `docs/frontend/`: one folder per application. Each contains `DESIGN.md` (architecture and stack), `STRUCTURE.md` (folders and files) and `SCHEMAS.md` (data schemas). Module documents such as `AUTH.md` are placed next to them.
  - `docs/ai/`: AI behavior across applications: RAG pipeline, LLM contracts, guardrails, evaluation. Code location is described in `docs/backend/STRUCTURE.md` and `docs/frontend/STRUCTURE.md`.
  - `docs/features/`: one specification per page.
- Each subsystem has its own `CLAUDE.md` with rules for its architecture and code. Read it before working in that subsystem.
- If a document has tradeoffs (rejected alternatives, limitations, pros and cons of a decision), they are placed in the `## Tradeoffs` section. The section is optional. If it exists, it is always the last section of the document, and the main text links to it.
- Prefer a single source of truth. Each fact is described in one document only. Other documents link to it instead of repeating it.
- If documentation, implementation and the rules in any `CLAUDE.md` disagree, do not resolve the conflict silently. List each discrepancy for the Engineer to fix: the files involved, what each one states and the suggested correction.

## 2. Language

- Only English is used in this repository: rules, documentation, code, comments, commit messages and any other text.

## 3. Claude Harness

Tasks are executed with the Claude Harness: roles Engineer, Planner, Executor and Validator, a state machine and enforced write rules. Entry point: [.claude/CLAUDE.md](.claude/CLAUDE.md). Role instructions: `.claude/skills/<Role>/SKILL.md`.

The rules below are specific to this project and take precedence over `.claude/CLAUDE.md`.

### Sources of truth

- `docs/` is the source of truth about the product and the architecture.
- The task artifacts (`TASK.md`, `PLAN.md`, `EXEC.md`, `VALIDATION.md`, `STATE.yaml`, `LOG.md` in `.claude/tasks/`) are the memory of one task and the instructions for its execution only. They do not define the product or the architecture.
- Where `.claude/CLAUDE.md` calls the task artifacts the only source of truth, it means the execution state of the task.
- If a task artifact contradicts `docs/`, `docs/` wins. A change of the product or the architecture starts with a change in `docs/`, see section 1.

### Read access

- Every role (Planner, Executor, Validator) reads the `docs/` documents relevant to the task in addition to its artifacts in the Read/Write Matrix of `.claude/CLAUDE.md`.
- The Write columns of the matrix do not change.

### Validator

- The Validator checks the implementation against `docs/` in addition to `TASK.md` and `PLAN.md`. A discrepancy is reported as an issue, as required by section 1.
- The Validator runs the unit and integration tests of the affected modules. `make eval` is not a part of the validation in v1.0: the Engineer runs it manually, see [EVALUATION.md](docs/ai/EVALUATION.md#run).
- Failed tests or eval regressions are a FAIL with an issue of type `logic`.

### File names

- `TASK.md` in the repository root is the product requirements of the project.
- `TASK.md` inside a task folder in `.claude/tasks/` is a harness artifact: the requirements of one task. The two files are not related.
