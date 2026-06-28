---
description: Validate repository changes with the narrowest useful checks first.
agent: tester
subtask: true
---

Verify current repository changes.

Task/context: $ARGUMENTS

Rules:
- Do not edit source files unless explicitly asked.
- Run safe validation commands only.
- Do not install dependencies without approval.
- Do not deploy.

Workflow:
1. Inspect git diff.
2. Detect package manager.
3. Detect available scripts.
4. Run the narrowest useful validation first.
5. Run broader validation if safe:
   - lint
   - typecheck
   - unit tests
   - integration tests
   - build
6. Use Graphify impact check if available.
7. Write validation report.

Report:
- changed files
- commands run
- pass/fail
- failures
- likely cause
- whether safe to merge
- recommended next action
