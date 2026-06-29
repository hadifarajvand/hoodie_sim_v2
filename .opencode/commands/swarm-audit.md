---
description: Full repository audit through RuFlo hierarchical coordinator with learning loop
agent: build
---

# /swarm-audit

Audit target: $ARGUMENTS

Use full RuFlo coordinator mode.

## Lifecycle

1. session-start / restore
2. memory search
3. route hook
4. Graphify lookup
5. spawn the needed audit agents
6. dispatch selective workers
7. perform audit checks
8. store findings and outcome
9. feedback store
10. post-task hook
11. session-end

## Initialize or reuse

```bash
npx ruflo@latest daemon status || npx ruflo@latest daemon start || true
npx ruflo@latest hive-mind status || npx ruflo@latest hive-mind init --topology hierarchical-mesh --max-agents 10 --queen-id coordinator --consensus raft || true
npx ruflo@latest swarm status || true
npx ruflo@latest hooks session-start || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace project-rules --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace decisions --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace patterns --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace failures --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace tasks --limit 5 || true
npx ruflo@latest hooks route --task "$ARGUMENTS" || true
npx ruflo@latest hooks explain --task "$ARGUMENTS" || true
npx ruflo@latest hooks pre-task --description "$ARGUMENTS" || true
```

## Spawn or reuse agents

```bash
npx ruflo@latest agent spawn -t hierarchical-coordinator --name coordinator || true
npx ruflo@latest agent spawn -t researcher --name researcher || true
npx ruflo@latest agent spawn -t system-architect --name system-architect || true
npx ruflo@latest agent spawn -t code-analyzer --name code-analyzer || true
npx ruflo@latest agent spawn -t reviewer --name reviewer || true
npx ruflo@latest agent spawn -t security-auditor --name security-auditor || true
npx ruflo@latest agent spawn -t performance-engineer --name performance-engineer || true
npx ruflo@latest agent spawn -t tester --name tester || true
npx ruflo@latest agent spawn -t memory-specialist --name memory-specialist || true
```

## Selective workers

```bash
npx ruflo@latest hooks worker dispatch --trigger audit --priority high || true
npx ruflo@latest hooks worker dispatch --trigger testgaps --priority normal || true
npx ruflo@latest hooks worker dispatch --trigger deepdive --context "$ARGUMENTS" --priority normal || true
npx ruflo@latest hooks worker dispatch --trigger optimize --priority normal || true
```

Use optimize only if performance is relevant.

## Audit scope

- architecture
- code quality
- security
- performance
- tests
- deployment readiness
- maintainability
- documentation
- MCP/tool exposure

## Storage

```bash
npx ruflo@latest memory store \
  --namespace tasks \
  --key "<task-slug>-audit-outcome" \
  --value "Task: $ARGUMENTS. Route: <agents-used>. Files: <files>. Validation: <commands-results>. Result: <success-or-failure>. Lesson: <lesson>." \
  --tags "task,outcome,audit" || true

npx ruflo@latest memory store \
  --namespace security \
  --key "<task-slug>-audit-security" \
  --value "<security summary or 'none'>" \
  --tags "security,audit" || true

npx ruflo@latest memory store \
  --namespace testing \
  --key "<task-slug>-audit-testing" \
  --value "<testing summary or 'none'>" \
  --tags "testing,audit" || true

npx ruflo@latest memory store \
  --namespace patterns \
  --key "<task-slug>-audit-pattern" \
  --value "<reusable pattern learned, or 'none'>" \
  --tags "pattern,audit,learned" || true

npx ruflo@latest memory store \
  --namespace decisions \
  --key "<task-slug>-audit-decision" \
  --value "<architectural decision if made, otherwise 'none'>" \
  --tags "decision,audit" || true

npx ruflo@latest memory store \
  --namespace feedback \
  --key "<task-slug>-audit-feedback" \
  --value "Quality: <0.00-1.00>. Route: <agents-used>. What worked: <summary>. What failed: <summary>. Next improvement: <summary>." \
  --tags "feedback,audit,quality" || true

npx ruflo@latest hooks post-task \
  --task-id "<task-slug>" \
  --success <true-or-false> \
  --quality <0.00-1.00> \
  --store-results true || true

npx ruflo@latest hooks session-end || true
```

## Output

- executive summary
- critical/high/medium/low findings
- quick wins
- required fixes
- suggested plan files
- memory/log entries
