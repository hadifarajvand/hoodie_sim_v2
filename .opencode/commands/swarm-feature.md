---
description: Coordinate a multi-agent feature workflow with Graphify and RuFlo.
agent: coordinator
subtask: true
---

Use RuFlo-style multi-agent workflow for a feature or medium/large implementation.

Task: $ARGUMENTS

Rules:
- Coordinator controls scope.
- Graph analyst identifies architecture and impact.
- Coder edits application files.
- Tester may edit tests.
- Reviewer is read-only.
- Security auditor is read-only unless explicitly asked.
- Do not let multiple agents edit the same file concurrently.
- Do not deploy or commit.

Required roles:
1. coordinator
2. graph-analyst
3. coder
4. tester
5. reviewer
6. security-auditor only if auth/payment/backend/secrets/deployment are touched

Workflow:
1. Read AGENTS.md.
2. Read docs/ai-stack/STACK_OVERVIEW.md.
3. Find or create plan under docs/plans/.
4. Run Graphify query/search if available.
5. Search RuFlo memory if available.
6. Implement according to the plan.
7. Run validation.
8. Reviewer checks diff.
9. Security auditor checks if needed.
10. Store outcome in run log and RuFlo memory if available.

Completion requires:
- diff summary
- validation result
- reviewer result
- security result if applicable
- remaining risks
