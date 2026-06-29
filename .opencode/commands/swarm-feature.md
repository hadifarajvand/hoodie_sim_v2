---
description: Feature implementation through RuFlo hierarchical coordinator with learning loop
agent: build
---

# /swarm-feature

Feature task: $ARGUMENTS

Use full RuFlo hierarchical coordinator mode.

## Lifecycle

1. session-start / restore
2. memory search
3. route hook
4. Graphify lookup
5. spawn the needed RuFlo built-in agents
6. create or update a plan
7. implement from plan
8. validate and review
9. write the run-log instruction
10. store outcome, pattern, and feedback
11. post-task hook
12. session-end

## Required baseline

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
npx ruflo@latest agent spawn -t planner --name planner || true
npx ruflo@latest agent spawn -t coder --name coder || true
npx ruflo@latest agent spawn -t tester --name tester || true
npx ruflo@latest agent spawn -t reviewer --name reviewer || true
npx ruflo@latest agent spawn -t memory-specialist --name memory-specialist || true
```

Add only if needed:

```bash
npx ruflo@latest agent spawn -t backend-dev --name backend-dev || true
npx ruflo@latest agent spawn -t system-architect --name system-architect || true
npx ruflo@latest agent spawn -t code-analyzer --name code-analyzer || true
npx ruflo@latest agent spawn -t security-auditor --name security-auditor || true
npx ruflo@latest agent spawn -t performance-engineer --name performance-engineer || true
```

## Workflow

1. Use Graphify to map feature impact and dependency radius.
2. Search RuFlo memory.
3. Create or update the plan.
4. Implement with coder and any required domain agent only.
5. Tester handles validation.
6. Reviewer checks the diff.
7. Security-auditor joins if sensitive.
8. Store memory and feedback.
9. Run the post-task hook.
10. End the session.

## Learning storage

```bash
npx ruflo@latest memory store \
  --namespace tasks \
  --key "<task-slug>-outcome" \
  --value "Task: $ARGUMENTS. Route: <agents-used>. Files: <files-changed>. Validation: <commands-results>. Result: <success-or-failure>. Lesson: <lesson>." \
  --tags "task,outcome,route" || true

npx ruflo@latest memory store \
  --namespace patterns \
  --key "<task-slug>-pattern" \
  --value "<reusable pattern learned, or 'none'>" \
  --tags "pattern,learned" || true

npx ruflo@latest memory store \
  --namespace feedback \
  --key "<task-slug>-feedback" \
  --value "Quality: <0.00-1.00>. Route: <agents-used>. What worked: <summary>. What failed: <summary>. Next improvement: <summary>." \
  --tags "feedback,routing,quality" || true

npx ruflo@latest hooks post-task \
  --task-id "<task-slug>" \
  --success <true-or-false> \
  --quality <0.00-1.00> \
  --store-results true || true

npx ruflo@latest hooks session-end || true
```

## Final output

- agents used
- plan path
- files changed
- tests run
- review result
- memory stored
