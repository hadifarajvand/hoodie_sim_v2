---
description: Review current changes without editing.
agent: reviewer
subtask: true
---

Review current changes without editing.

Task/context: $ARGUMENTS

Rules:
- No edits.
- No destructive commands.
- No production actions.

Review:
1. git diff
2. changed files
3. tests added/updated
4. architecture impact
5. security impact
6. performance impact
7. maintainability
8. scope creep

Output:
- approved / changes requested
- blocking issues
- non-blocking issues
- test gaps
- risk level
