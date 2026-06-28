---
description: Create a scoped implementation plan without editing files.
agent: plan
subtask: true
---

You are planning only. Do not edit files.

Task: $ARGUMENTS

Steps:
1. Inspect the repository safely.
2. Read AGENTS.md and docs/ai-stack/STACK_OVERVIEW.md if present.
3. Identify scope, assumptions, likely files, risks, and validation commands.
4. Create or update a plan file under `docs/plans/`.

Plan file name:
- use a slug from the task
- format: `docs/plans/YYYY-MM-DD-<task-slug>.md`

Plan must include:
- objective
- non-goals
- current understanding
- affected files/modules
- Graphify needed? yes/no
- RuFlo needed? yes/no
- agent roles needed
- implementation steps
- validation gates
- rollback strategy
- risks
- acceptance criteria

Rules:
- no code edits
- no dependency installation
- no destructive commands
- no production actions
