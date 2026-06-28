---
description: Prepare a production readiness check without deploying.
agent: coordinator
subtask: true
---

Prepare a production readiness check. Do not deploy.

Target: $ARGUMENTS

Rules:
- No production deployment.
- No DNS/billing/cloud mutation.
- No secret rotation.
- No database production migration.
- No destructive commands.
- Read-only unless explicitly asked.

Check:
1. git diff
2. tests/build/lint/typecheck
3. environment variable documentation without reading secret values
4. migration risk
5. deployment config
6. rollback plan
7. logs/monitoring readiness
8. security review
9. manual approval checklist

Output:
- ready / not ready
- blockers
- risks
- commands already run
- commands still needed
- rollback plan
- human approval checklist
