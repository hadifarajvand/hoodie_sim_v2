---
description: Planning only with RuFlo memory, routing, and graph awareness
agent: plan
---

# /plan

Task: $ARGUMENTS

Planning only. No code edits.

## Lifecycle

1. session-start / restore
2. memory search
3. route hook
4. Graphify lookup if useful
5. spawn the planning agents
6. create or update the plan
7. store decision or useful planning outcome
8. feedback store
9. post-task hook if planning created a durable project decision
10. session-end

## Required behavior

- Check RuFlo daemon and hive status.
- Start the daemon only if stopped.
- Do not reinitialize an existing hive.
- Use RuFlo built-in agents only.
- Do not edit application code.
- Do not add per-agent overrides.

## Required agents

```bash
npx ruflo@latest agent spawn -t hierarchical-coordinator --name coordinator || true
npx ruflo@latest agent spawn -t planner --name planner || true
npx ruflo@latest agent spawn -t memory-specialist --name memory-specialist || true
```

Add `researcher` only if external/docs investigation is needed.

## Commands to run

```bash
npx ruflo@latest daemon status || npx ruflo@latest daemon start || true
npx ruflo@latest hive-mind status || true
npx ruflo@latest swarm status || true
npx ruflo@latest hooks session-start || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace project-rules --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace decisions --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace patterns --limit 5 || true
npx ruflo@latest memory search --query "$ARGUMENTS" --namespace failures --limit 5 || true
npx ruflo@latest hooks route --task "$ARGUMENTS" || true
npx ruflo@latest hooks explain --task "$ARGUMENTS" || true
npx ruflo@latest hooks pre-task --description "$ARGUMENTS" || true
```

Use Graphify if the task is cross-module, architectural, or risk-sensitive. Capture:
- affected files/modules
- dependency paths
- impact radius
- validation gates

## Plan file

Create or update:

```text
docs/plans/YYYY-MM-DD-<task-slug>.md
```

The plan must include:
- objective
- non-goals
- task classification
- RuFlo routing result
- memory findings
- Graphify findings if used
- affected files/modules
- selected RuFlo built-in agents for implementation
- implementation steps
- validation gates
- rollback strategy
- risks
- acceptance criteria

If planning creates a useful project decision, store it in memory:

```bash
npx ruflo@latest memory store \
  --namespace decisions \
  --key "<task-slug>-decision" \
  --value "Decision: <decision>. Context: <context>. Impact: <impact>. Reason: <why>." \
  --tags "decision,planning" || true

npx ruflo@latest memory store \
  --namespace feedback \
  --key "<task-slug>-planning-feedback" \
  --value "Quality: <0.00-1.00>. Route: <agents-used>. What worked: <summary>. What failed: <summary>. Next improvement: <summary>." \
  --tags "feedback,planning,quality" || true
```

Final answer:
- plan path
- memory findings
- route recommendation
- Graphify summary
- next command
