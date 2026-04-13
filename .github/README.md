# `.github` Governance

This directory contains repo-local governance files for instruction-aware coding agents.

## What this setup does

- Gives the agent a repo-wide operating contract through `copilot-instructions.md`
- Adds focused personas under `agents/`
- Supports stack-specific overlays under `instructions/`
- Provides reusable prompts under `prompts/`
- Creates task-memory files under `tasks/` so planning, verification, and lessons stay visible

## Included directories

- `agents/`
  - focused personas for architecture, testing, security, operations, and migrations
- `instructions/`
  - path-scoped guidance files; add only the packs that match the repo
- `prompts/`
  - reusable prompts for repo bootstrap, project init, branch review, and incident debugging
- `tasks/`
  - `todo.md` for the active task and `lessons.md` for recurring prevention rules

## Model compatibility

- This setup is instruction-driven and works best in instruction-aware chat or agent flows.
- It can be used with explicit model selection or with Auto.
- In Auto mode, model choice may vary by task, while `.github` instructions should still be applied by the agent layer.

## How to use after setup

1. Start sessions by reading `AGENTS.md`, `.github/copilot-instructions.md`, relevant stack packs, and `.github/tasks/lessons.md`.
2. Initialize or update `.github/tasks/todo.md` before implementation edits.
3. Use the prompt files in `prompts/` for recurring workflows.
4. Use the focused personas in `agents/` when a task benefits from a specific review lens.

## Minimal validation flow

1. Ask the agent to perform a non-trivial task.
2. Confirm it starts with a plan and codebase intake.
3. Confirm `.github/tasks/todo.md` is updated as work progresses.
4. Confirm completion includes fresh verification evidence.
5. Correct the agent once and confirm a same-turn lessons entry appears in `.github/tasks/lessons.md`.

## References

- [12 Factor App](https://12factor.net/)
- [C4 Model](https://c4model.com/)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [Feature Toggles](https://martinfowler.com/articles/feature-toggles.html)
