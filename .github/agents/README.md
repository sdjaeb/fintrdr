# Agent Personas

Use these personas when a task benefits from a specific lens.

## Which agent to pick

| Agent | Use when | Primary focus |
| --- | --- | --- |
| `@staff-architect` | design, implementation planning, root-cause fixes | architecture coherence and delivery discipline |
| `@test-engineer` | test gaps, deterministic coverage, testability | focused test design and evidence |
| `@security-reviewer` | diff review, secrets, PII, unsafe patterns | security and privacy findings |
| `@ops-sre` | incidents, alerts, reliability, rollback planning | operational safety and observability |
| `@migration-buddy` | staged rollouts, backfills, compatibility work | incremental migration strategy |

## Invocation examples

- `@staff-architect review this feature before I start editing`
- `@test-engineer add focused tests for the changed parser behavior`
- `@security-reviewer review this branch for secrets, unsafe input handling, and logging risks`
- `@ops-sre turn this incident into a short triage and rollback plan`
- `@migration-buddy propose a staged rollout plan for replacing this legacy service`

## Customizing agents

When the architecture or team workflow changes:

- add or replace domain expertise bullets
- update trade-off guidance to reflect the new constraints
- update done criteria and verification checks
- add one new usage example for each major capability you introduce
- remove assumptions that no longer match the repo
