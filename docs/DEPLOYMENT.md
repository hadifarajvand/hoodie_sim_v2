# Deployment Policy

Agents do not deploy production by default.

Agents may:
- inspect deployment config
- inspect CI status
- inspect logs if read-only access is available
- prepare release checklist
- propose rollback plan

Agents may not:
- deploy production
- mutate DNS
- mutate billing
- rotate secrets
- change production database
- modify cloud infrastructure

Production requires human approval.
