---
description: Graph-first planning through Graphify plus RuFlo coordinator and memory
agent: build
---

# /graph-plan

Task: $ARGUMENTS

Graphify first. No implementation.

## Lifecycle

1. session-start / restore
2. memory search
3. route hook
4. Graphify lookup and dependency analysis
5. spawn graph/planning agents
6. create or update a plan
7. store decision or graph insight if useful
8. feedback store
9. post-task hook if a durable planning result was produced
10. session-end

## Required agents

```bash
npx ruflo@latest agent spawn -t hierarchical-coordinator --name coordinator || true
npx ruflo@latest agent spawn -t planner --name planner || true
npx ruflo@latest agent spawn -t memory-specialist --name memory-specialist || true
npx ruflo@latest agent spawn -t system-architect --name system-architect || true
npx ruflo@latest agent spawn -t code-analyzer --name code-analyzer || true
```

Add `researcher` only if needed.

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

## Graphify questions

- Which files implement this area?
- What depends on this?
- What path connects relevant modules?
- What is the impact radius?
- What tests are related?

If `graphify-out/graph.json` exists or Graphify tooling is available, use it first. If not, fall back to read-only repository search.

## Plan file

Create or update:

```text
docs/plans/YYYY-MM-DD-<task-slug>.md
```

The plan must include:
- Graphify findings
- affected nodes/files/modules
- dependency paths
- impact radius
- routing result
- memory findings
- selected built-in RuFlo agents
- implementation order
- validation gates
- security/production risks
- acceptance criteria

If the graph work yields a durable decision, store it in memory:

```bash
npx ruflo@latest memory store \
  --namespace decisions \
  --key "<task-slug>-graph-decision" \
  --value "Decision: <decision>. Graph: <nodes-paths>. Impact: <radius>. Reason: <why>." \
  --tags "decision,graph,planning" || true

npx ruflo@latest memory store \
  --namespace patterns \
  --key "<task-slug>-graph-pattern" \
  --value "<reusable graph/planning pattern, or 'none'>" \
  --tags "pattern,graph,learned" || true

npx ruflo@latest memory store \
  --namespace feedback \
  --key "<task-slug>-graph-feedback" \
  --value "Quality: <0.00-1.00>. Route: <agents-used>. What worked: <summary>. What failed: <summary>. Next improvement: <summary>." \
  --tags "feedback,graph,quality" || true
```

Final answer:
- graph findings
- plan path
- route recommendation
- next command
