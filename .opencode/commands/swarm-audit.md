---
description: Run a read-only multi-agent audit.
agent: coordinator
subtask: true
---

Run a multi-agent audit.

Audit target: $ARGUMENTS

Use roles:
- coordinator
- graph-analyst
- reviewer
- security-auditor
- performance-engineer
- tester

Rules:
- Default read-only.
- Do not edit unless explicitly asked.
- Do not deploy.
- Do not read secrets.

Audit dimensions:
1. architecture
2. correctness
3. security
4. performance
5. tests
6. deployment readiness
7. maintainability
8. documentation

Output:
- executive summary
- high-risk findings
- medium-risk findings
- low-risk findings
- quick wins
- required fixes
- proposed plan file under docs/plans/
