# Bootstrap Agentic Governance For A New Repo

Use this prompt in a new repository when you want the agent to create a concise governance baseline.

```text
Set up instruction-driven repository governance for this codebase.

Before writing files:
- detect the primary stack and workflow from the repository contents
- keep the result concise and practical
- avoid company-specific or environment-specific assumptions

Create:
- AGENTS.md
- .github/copilot-instructions.md
- .github/agents/*.agent.md for architecture, testing, security, ops, and migration work
- .github/instructions/*.instructions.md only for stacks actually present
- .github/prompts/ for init, branch review, and incident debugging
- .github/tasks/todo.md
- .github/tasks/lessons.md
- .github/README.md

Requirements:
- plan mode for non-trivial work
- codebase-first intake before edits
- task memory updates in .github/tasks/todo.md
- same-turn lessons entry after explicit user correction
- verification evidence before completion

After file creation, report:
- created files
- open assumptions
- validation steps to confirm the governance is active
```
