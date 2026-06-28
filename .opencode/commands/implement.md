---
description: Implement from an existing plan with minimal scoped edits.
agent: coder
subtask: true
---

Implement according to an existing plan.

Task / plan: $ARGUMENTS

Rules:
- Read the relevant plan first.
- If no plan exists and the task is not a tiny obvious fix, stop and create a plan.
- Make minimal changes.
- Do not perform unrelated cleanup.
- Do not edit secrets.
- Do not modify production resources.
- Do not commit.

Workflow:
1. Read AGENTS.md.
2. Read relevant plan in `docs/plans/`.
3. Identify exact files to change.
4. Implement smallest correct change.
5. Add/update tests if needed.
6. Run targeted validation if safe.
7. Write run log under `docs/run-logs/`.

Run log must include:
- task
- plan file used
- files changed
- commands run
- test result
- failures
- follow-up needed
