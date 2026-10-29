# CLAUDE.md

Claude Harness: the development process of the project. It is not a part of the product. The LLM Harness of the product: [HARNESS.md](HARNESS.md). Claude agents generate the code from the specifications in `docs/` and check it against them. The Engineer writes the task, approves high-risk plans and commits.

Entry point for the agents: [.claude/CLAUDE.md](../../.claude/CLAUDE.md). Project rules that take precedence over it: [CLAUDE.md](../../CLAUDE.md#3-claude-harness).

## Roles

| Role | Who | Output |
| --- | --- | --- |
| Engineer | Human | `TASK.md`, approval of HIGH plans, commit |
| Planner | Claude agent | `PLAN.md`: architecture and steps |
| Executor | Claude agent | Code and `EXEC.md` |
| Validator | Claude agent | `VALIDATION.md`: check of the code against `TASK.md`, `PLAN.md` and `docs/` |

Role instructions: `.claude/skills/<Role>/SKILL.md`.

## Task artifacts

Each task has a folder in `.claude/tasks/` with `TASK.md`, `PLAN.md`, `EXEC.md`, `VALIDATION.md`, `STATE.yaml` and `LOG.md`.

- The artifacts are the memory of the task. The chat history is not used as memory, so a task survives a cleared context window and can be resumed.
- `docs/` is the source of truth about the product and the architecture. If an artifact contradicts `docs/`, `docs/` wins.
- `PLAN.md`, `EXEC.md` and `VALIDATION.md` keep the previous versions as `## v<n>` blocks.
- Closed tasks are moved to `.claude/tasks/DONE/<YYYY-MM>/`. Examples of closed tasks: [.claude/tasks/DONE](../../.claude/tasks/DONE).

## Routing by complexity

The task complexity is set from `TASK.md`:

| Complexity | Criteria | Route |
| --- | --- | --- |
| LOW | One file, no new dependencies, no schema change | Engineer, Executor, Validator |
| MEDIUM | Several files or a new module | Engineer, Planner, Executor, Validator |
| HIGH | Schema, infrastructure, security or public API change | Engineer, Planner, Engineer approval, Executor, Validator |

`STATE.yaml` is the only routing source: stage, status, `next_actor`, iteration, open issues. One actor runs per invocation.

## Validation failures

- On FAIL the Validator copies each blocking issue into `STATE.yaml.open_issues` with its type.
- Routing by issue type: `requirement` to the Engineer, `architecture` to the Planner, `logic` to the Executor.
- At most 2 re-routes. After the second unresolved FAIL the task is `ESCALATED` to the Engineer.

## Enforcement

| Mechanism | File | What it checks |
| --- | --- | --- |
| `runner.py` | [.claude/runner.py](../../.claude/runner.py) | Task registry and dispatch: `new`, `list`, `use`, `status`, `next`, `done` |
| Write matrix hook | [.claude/hooks/enforce_matrix.py](../../.claude/hooks/enforce_matrix.py) | PreToolUse on Write and Edit: a role writes only its artifacts, `STATE.yaml` changes only by legal stage transitions |
| Pre-commit hook | [.claude/githooks/pre-commit](../../.claude/githooks/pre-commit) | Blocks a commit when the active task is `ESCALATED`, has open issues or is `DONE` and not closed. Runs the tests of the applications with staged changes: `make backend-test` for `backend/`, `pnpm lint`, `typecheck` and `test` for `frontend/`. `make eval` is not run: it makes real OpenAI calls |
| Repository check | [.claude/scripts/ci_check.py](../../.claude/scripts/ci_check.py) | No `ESCALATED` task, no open issues, `DONE` only with `PASS`. The CI workflow that runs it is not in the repository in v1.0 |

Settings: limits, complexity rules and modes in [.claude/SETTINGS.md](../../.claude/SETTINGS.md).

## Tradeoffs

- Cost: a MEDIUM task runs three agents instead of one. In return the code is checked against `docs/` before the Engineer reviews it, and a FAIL is routed to the role that caused it.
- Local hooks can be skipped with `--no-verify`. Only a CI gate is a hard barrier.
