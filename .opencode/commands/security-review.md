---
description: Security review using RuFlo security agents with memory learning
agent: plan
---

# /security-review

Target: $ARGUMENTS

Read-only security review.

Do not:
- edit files
- read secrets
- run destructive commands
- deploy
- mutate cloud/DNS/billing/database

## Lifecycle

1. session-start / restore
2. memory search for security, failures, and patterns
3. route hook
4. Graphify attack-surface and dependency-path lookup
5. spawn security agents
6. review read-only
7. store security findings
8. feedback store
9. post-task hook if this closes a security task
10. session-end

## Required agents

```bash
npx ruflo@latest agent spawn -t security-architect --name security-architect || true
npx ruflo@latest agent spawn -t security-auditor --name security-auditor || true
npx ruflo@latest agent spawn -t code-analyzer --name code-analyzer || true
```

## Commands to run

```bash
npx ruflo@latest hooks session-start || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace security --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace failures --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace patterns --limit 5 || true
npx ruflo@latest hooks route --task "$ARGUMENTS" || true
npx ruflo@latest hooks explain --task "$ARGUMENTS" || true
npx ruflo@latest hooks pre-task --description "$ARGUMENTS" || true
```

Use Graphify for attack surface and dependency paths if available. Do not read secrets.

## Check

- auth
- authorization
- session/cookies/tokens
- input validation
- database queries
- secrets exposure
- unsafe logging
- API routes
- SSRF/XSS/CSRF/injection
- dependency/config risk
- MCP/tool exposure
- deployment config

## Security storage

```bash
npx ruflo@latest memory store \
  --namespace security \
  --key "<task-slug>-security-findings" \
  --value "Findings: <summary>. Files: <files>. Severity: <severity>. Exploitability: <exploitability>. Fix: <recommended-fix>. Validation: <validation>." \
  --tags "security,review,findings" || true

npx ruflo@latest memory store \
  --namespace feedback \
  --key "<task-slug>-security-feedback" \
  --value "Quality: <0.00-1.00>. Route: <agents-used>. What worked: <summary>. What failed: <summary>. Next improvement: <summary>." \
  --tags "feedback,security,quality" || true

npx ruflo@latest hooks post-task \
  --task-id "<task-slug>" \
  --success <true-or-false> \
  --quality <0.00-1.00> \
  --store-results true || true

npx ruflo@latest hooks session-end || true
```

## Final output

- critical findings
- high findings
- medium findings
- low findings
- exact files/lines where possible
- exploitability
- recommended fix
- validation test
