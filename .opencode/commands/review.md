---
description: Read-only review using RuFlo reviewer and code-analyzer with memory learning
agent: plan
---

# /review

Context: $ARGUMENTS

Read-only review. Do not edit.

## Lifecycle

1. session-start / restore
2. memory search for failures, patterns, and prior review notes
3. route hook
4. Graphify lookup if the review spans modules
5. spawn review agents
6. review the diff read-only
7. store review feedback
8. feedback store
9. post-task hook if review closes the task
10. session-end

## Required agents

```bash
npx ruflo@latest agent spawn -t reviewer --name reviewer || true
npx ruflo@latest agent spawn -t code-analyzer --name code-analyzer || true
```

Add only when relevant:

```bash
npx ruflo@latest agent spawn -t security-auditor --name security-auditor || true
npx ruflo@latest agent spawn -t performance-engineer --name performance-engineer || true
```

## Review focus

- correctness
- edge cases
- regression risk
- architecture impact
- security
- performance
- maintainability
- tests
- scope creep
- deployment risk

## Commands to run

```bash
npx ruflo@latest hooks session-start || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace failures --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace patterns --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace decisions --limit 5 || true
npx ruflo@latest hooks route --task "$ARGUMENTS" || true
npx ruflo@latest hooks explain --task "$ARGUMENTS" || true
npx ruflo@latest hooks pre-task --description "$ARGUMENTS" || true
```

Use Graphify if cross-module impact exists. Record the dependency path and affected modules.

## Feedback storage

```bash
npx ruflo@latest memory store \
  --namespace feedback \
  --key "<task-slug>-review-feedback" \
  --value "Quality: <0.00-1.00>. Route: <agents-used>. What worked: <summary>. What failed: <summary>. Next improvement: <summary>. Findings: <summary>." \
  --tags "feedback,review,quality" || true

npx ruflo@latest hooks post-task \
  --task-id "<task-slug>" \
  --success <true-or-false> \
  --quality <0.00-1.00> \
  --store-results true || true

npx ruflo@latest hooks session-end || true
```

## Final output

- approved / changes requested
- blocking issues
- non-blocking issues
- test gaps
- risk level
- next command
