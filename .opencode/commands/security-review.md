---
description: Perform a read-only security review of the current changes.
agent: security-auditor
subtask: true
---

Perform read-only security review.

Task/context: $ARGUMENTS

Rules:
- Do not edit files.
- Do not read secrets.
- Do not run destructive commands.
- Do not deploy.

Check:
- auth
- authorization
- session/cookies/tokens
- input validation
- database queries
- logging
- secrets exposure
- dependency/config risk
- API routes
- SSRF/XSS/CSRF/injection
- MCP/tool exposure
- deployment config

Output:
- critical/high/medium/low findings
- exact files/lines where possible
- exploitability
- recommended fix
- validation test
