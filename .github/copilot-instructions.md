# Repo Instructions

## Purpose

Use this file as the repo-wide operating contract for instruction-aware coding agents.

At session start, infer the actual product purpose, stack, architecture, and validation commands from the current repository instead of guessing from prior sessions.

## Project Discovery

- Read `AGENTS.md` if present.
- Read this file and any relevant `.github/instructions/*.instructions.md` files.
- Read `.github/tasks/lessons.md` before starting non-trivial work.
- Inspect the codebase broadly first, then narrow to the files and symbols that matter.
- Identify the repo commands for build, lint, type check, test, and local run before editing.

## Workflow Orchestration Defaults

- Plan mode by default for non-trivial work.
- Challenge assumptions before editing.
- Start broad with codebase or workspace context, then narrow with specific files and symbols.
- Update `.github/tasks/todo.md` with scope, plan, and verification steps before substantial edits.
- Interrupt early and re-plan when new evidence contradicts the current model.
- Use one fresh session per feature or unrelated problem.
- Use parallel sessions only with explicit ownership and non-overlapping edits.
- Use specialist agents or skills only for bounded tasks; keep final integration reasoning in the primary session.
- Do not mark work complete without verification evidence tied to the final state.
- If logs, failing tests, or concrete bug reports are provided, drive to root cause before proposing a fix.

## Implementation Expectations

- Preserve existing architecture boundaries unless the task explicitly changes them.
- Prefer small, root-cause-focused changes over wide rewrites.
- Keep interfaces clear and error handling explicit.
- Avoid secrets or sensitive data in code, tests, logs, and examples.
- Keep documentation and operational guidance aligned with behavior changes.
- If stack-specific packs exist, follow them instead of restating the same rules here.

## Testing And Verification

- Add or update focused tests for changed behavior.
- Prefer deterministic tests with clear fixtures and small scopes.
- For changed code, aim for high changed-line confidence and explain known gaps.
- Re-run relevant validation after the final edit, not just before it.
- If full validation is not possible, say exactly what remains unverified.

## Security And Privacy

- Never commit secrets, tokens, or internal credentials.
- Redact sensitive values in logs and examples.
- Validate inputs and outputs explicitly.
- Apply least privilege to permissions and infrastructure changes.
- Treat production-impacting operational changes as needing rollback awareness.

## Git And Review Hygiene

- Keep commits and pull requests small when practical.
- Use conventional commits if the repo uses them.
- When reviewing, lead with findings and risks rather than summaries.
- Do not invent test, rollout, or coverage evidence.

## Rules Maintenance

- When the user says a recurring mistake should not happen again, update the relevant governance file rather than leaving the rule only in chat.
- Prefer high-signal rules. Move stack specifics into `.github/instructions/` instead of bloating this file.

## Lessons Entry Contract (Required)

When a user correction is explicit, append exactly one new entry to `.github/tasks/lessons.md` using this template:

```markdown
### YYYY-MM-DD — <short title>
- Context:
  - <task and scope>
- What went wrong:
  - <specific mistake>
- Root cause:
  - <why it happened>
- Prevention rule:
  - <future rule to prevent recurrence>
- Validation step added:
  - <specific check that proves compliance>
```

Rules:

- Write the entry in the same turn as the correction.
- Keep each field concrete and testable.
- Link the prevention rule to at least one verification step in `.github/tasks/todo.md`.

## Usage Hints

- Use repo-wide context first for unfamiliar codebases.
- Attach relevant diffs, logs, failing tests, and config when asking for help.
- Inline completions often ignore these instructions; chat or agent flows are more reliable for instruction-aware work.
