# Agent Playbook

This file provides a shared workflow contract for coding agents working in this repository.

## Default Persona

- Use: `.github/agents/staff-architect.agent.md`
- Supporting standards:
  - `.github/copilot-instructions.md`
  - relevant `.github/instructions/*.instructions.md`

## Mandatory Task Memory Loop

1. At task start, read `.github/tasks/lessons.md` and apply relevant prevention rules.
2. Create or update `.github/tasks/todo.md` with:
   - scope and constraints
   - a checkable plan
   - verification steps
3. During execution, keep `todo.md` current with commands run and outcomes.
4. After an explicit user correction, append one new structured lessons entry in the same turn and add a matching validation step to `todo.md`.

## Session Discipline

- Start in plan mode by default for any non-trivial task.
- Treat session bootstrap as mandatory: `AGENTS.md`, `.github/` guidance, `lessons.md`, then initialize `todo.md`.
- Challenge assumptions before editing.
- Interrupt early when evidence contradicts the current plan; stop, update the plan, and continue only after the correction is reflected.
- Use one clean session per feature or problem area.
- Use parallel sessions only with explicit ownership and non-overlapping edits.
- Use specialist agents only for atomic tasks; keep cross-cutting reasoning in the primary session.

## Delivery Gates

- Prefer minimal root-cause fixes over broad rewrites.
- Add or update tests for changed behavior.
- Provide verification evidence before marking work complete.
- Keep generated artifacts under repo `tmp/` unless the user asks for a different location.
