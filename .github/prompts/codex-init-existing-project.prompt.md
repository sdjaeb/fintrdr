# Codex Init For An Existing Project

Use this prompt at the beginning of a new session in an existing repository.

```text
Treat this as project init.

Goals:
- build an accurate model of the current codebase and workflow rules
- ensure governance files are aligned before implementation work starts

Steps:
1. Read AGENTS.md if present, .github/copilot-instructions.md, relevant .github/instructions/*.instructions.md, and .github/agents/*.agent.md.
2. Scan the codebase broadly before narrowing to the active files and symbols.
3. Read .github/tasks/lessons.md and apply relevant prevention rules.
4. Initialize or update .github/tasks/todo.md with scope, constraints, a checkable plan, and verification steps.
5. Identify the repo commands for lint, type check, tests, build, and local run.
6. Report the stack summary, validation commands, open assumptions, and any stale governance files before coding.

Do not modify runtime application code during this init pass unless the user explicitly asks for it.
```
