---
description: Read-only production readiness check using RuFlo production agents with learning
agent: plan
---

# /production-check

Target: $ARGUMENTS

Read-only unless explicitly approved.

Do not:
- deploy production
- mutate DNS
- mutate billing
- rotate secrets
- change production database
- modify cloud infrastructure
- commit/push

## Lifecycle

1. session-start / restore
2. memory search
3. route hook
4. Graphify lookup if deployment touches shared modules
5. spawn production agents
6. review readiness read-only
7. store readiness result
8. feedback store
9. post-task hook if readiness review completes the task
10. session-end

## Required agents

```bash
npx ruflo@latest agent spawn -t production-validator --name production-validator || true
npx ruflo@latest agent spawn -t security-auditor --name security-auditor || true
npx ruflo@latest agent spawn -t reviewer --name reviewer || true
npx ruflo@latest agent spawn -t tester --name tester || true
```

## Commands to run

```bash
npx ruflo@latest hooks session-start || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace deployment --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace security --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace patterns --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace failures --limit 5 || true
npx ruflo@latest hooks route --task "$ARGUMENTS" || true
npx ruflo@latest hooks explain --task "$ARGUMENTS" || true
npx ruflo@latest hooks pre-task --description "$ARGUMENTS" || true
```

## Check

1. git diff
2. CI/test/build/lint/typecheck status
3. deployment config without reading secrets
4. env var documentation without secret values
5. migration risk
6. rollback plan
7. monitoring/logging
8. security review
9. manual approval checklist

## Storage

```bash
npx ruflo@latest memory store \
  --namespace deployment \
  --key "<task-slug>-production-readiness" \
  --value "Ready: <ready-or-not-ready>. Blockers: <blockers>. Risks: <risks>. Commands: <commands>. Needed: <commands-still-needed>. Rollback: <rollback-plan>." \
  --tags "deployment,production,readiness" || true

npx ruflo@latest memory store \
  --namespace feedback \
  --key "<task-slug>-production-feedback" \
  --value "Quality: <0.00-1.00>. Route: <agents-used>. What worked: <summary>. What failed: <summary>. Next improvement: <summary>." \
  --tags "feedback,production,quality" || true

npx ruflo@latest hooks post-task \
  --task-id "<task-slug>" \
  --success <true-or-false> \
  --quality <0.00-1.00> \
  --store-results true || true

npx ruflo@latest hooks session-end || true
```

## Final output

- ready / not ready
- blockers
- risks
- commands run
- commands still needed
- rollback plan
- human approval checklist
